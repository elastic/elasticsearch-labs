from elasticsearch import Elasticsearch
from lib.elasticsearch_chat_message_history import ElasticsearchChatMessageHistory
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.prompts.prompt import PromptTemplate
from langchain.vectorstores import ElasticsearchStore
from langchain.docstore.document import Document
from queue import Queue
from uuid import uuid4
import json
import os
import threading
from dotenv import load_dotenv
load_dotenv()

INDEX = os.getenv("ELASTIC_INDEX")
INDEX_CHAT_HISTORY = INDEX + "-chat-history"
ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

POISON_MESSAGE = "~~~END~~~"
SESSION_ID_TAG = "[SESSION_ID]"
SOURCE_TAG = "[SOURCE]"
DONE_TAG = "[DONE]"

def query(self):
    def _query(
         query_vector,
         query,
         k,
         fetch_k,
         vector_query_field,
         text_field,
         filter,
         similarity,
    ):
        return {
             "query": {
                 "bool": {
                     "must": [
                         {
                             "text_expansion": {
                                 vector_query_field: {
                                     "model_id": self.model_id,
                                     "model_text": query,
                                 }
                             }
                         }
                     ],
                     "filter": filter,
                 }
             }
        }

    return _query

def search(self):
    def _search(
       query = None,
       k = 4,
       query_vector = None,
       fetch_k = 50,
       fields = None,
       filter = None,
       custom_query = None):
        if fields is None:
            fields = ["title", "url", "last_crawled_at", "website_area"]

        if self.query_field not in fields:
            fields.append(self.query_field)

        if self.embedding and query is not None:
            query_vector = self.embedding.embed_query(query)

        query_body = self.strategy.query(
            query_vector=query_vector,
            query=query,
            k=k,
            fetch_k=fetch_k,
            vector_query_field=self.vector_query_field,
            text_field=self.query_field,
            filter=filter or [],
            similarity=self.distance_strategy,
        )

        if custom_query is not None:
            query_body = custom_query(query_body, query)

        response = self.client.search(
            index=self.index_name,
            **query_body,
            size=k,
            source=fields,
        )

        hits = [hit for hit in response["hits"]["hits"]]

        docs_and_scores = [
            (
                Document(
                    page_content=hit["_source"][self.query_field],
                    metadata=hit["_source"],
                ),
                hit["_score"],
            )
            for hit in hits
        ]

        return docs_and_scores

    return _search

strategy = ElasticsearchStore.SparseVectorRetrievalStrategy()
strategy.query = query(strategy)

class QueueCallbackHandler(BaseCallbackHandler):
    def __init__(
        self,
        queue: Queue,
    ):
        self.queue = queue
        self.in_human_prompt = True

    def on_retriever_end(self, documents, *, run_id, parent_run_id=None, **kwargs):
        if len(documents) > 0:
            for doc in documents:
                source = {
                    "name": doc.metadata["title"],
                    "page_content": doc.page_content,
                    "url": doc.metadata["url"],
                    "updated_at": doc.metadata["last_crawled_at"],
                    "icon": doc.metadata["website_area"],
                }
                self.queue.put(f"{SOURCE_TAG} {json.dumps(source)}")

    def on_llm_new_token(self, token, **kwargs):
        if not self.in_human_prompt:
            self.queue.put(token)

    def on_llm_start(
        self,
        serialized,
        prompts,
        *,
        run_id,
        parent_run_id=None,
        tags=None,
        metadata=None,
        **kwargs,
    ):
        self.in_human_prompt = prompts[0].startswith("Human:")

    def on_llm_end(self, response, *, run_id, parent_run_id=None, **kwargs):
        if not self.in_human_prompt:
            self.queue.put(POISON_MESSAGE)


elasticsearch_client = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID, basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)

store = ElasticsearchStore(
    es_connection=elasticsearch_client,
    index_name=INDEX,
    strategy=strategy,
    vector_query_field="ml.inference.body_expanded.predicted_value",
    query_field="body"
)
store._search = search(store)

retriever = store.as_retriever()

llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, streaming=True, temperature=0.2)

general_system_template = """ 
Use the following passages to answer the user's question.
Each passage has a SOURCE which is the title of the document. When answering, give the source name of the passages you are answering from, put them as an array of strings in here <script>[sources]</script>.
Don't mention the sources of passages in answer until it contains in source.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

----
{context}
----

"""
general_user_template = "Question: {question}"
qa_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
    ]
)

document_prompt = PromptTemplate(
    input_variables=["page_content", "title"],
    template="""
---
NAME: "{title}"
PASSAGE: 
{page_content}
---
""",
)

chat = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=store.as_retriever(),
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": qa_prompt, "document_prompt": document_prompt},
    verbose=True,
)

app = Flask(__name__, static_folder="../frontend/public")
CORS(app)


@app.route("/")
def api_index():
    return app.send_static_file("index.html")


def ask_question(question, queue, chat_history):
    result = chat(
        {"question": question, "chat_history": chat_history.messages},
        callbacks=[QueueCallbackHandler(queue)],
    )

    chat_history.add_user_message(result["question"])
    chat_history.add_ai_message(result["answer"])


@app.route("/api/chat", methods=["POST"])
def api_chat():
    stream_queue = Queue()
    request_json = request.get_json()
    question = request_json.get("question")
    if question is None:
        return jsonify({"msg": "Missing question from request JSON"}), 400

    session_id = request.args.get("session_id", str(uuid4()))

    print("Chat session ID: ", session_id)
    chat_history = ElasticsearchChatMessageHistory(
        client=elasticsearch_client, index=INDEX_CHAT_HISTORY, session_id=session_id
    )

    def generate(queue: Queue):
        yield f"data: {SESSION_ID_TAG} {session_id}\n\n"

        message = None
        while True:
            message = queue.get()

            if message == POISON_MESSAGE:  # Poison message
                break
            yield f"data: {message}\n\n"

        yield f"data: {DONE_TAG}\n\n"

    threading.Thread(
        target=ask_question, args=(question, stream_queue, chat_history)
    ).start()

    return Response(generate(stream_queue), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(port=3001, debug=True)
