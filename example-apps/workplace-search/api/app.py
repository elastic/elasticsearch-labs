from elasticsearch import Elasticsearch
from lib.elasticsearch_chat_message_history import ElasticsearchChatMessageHistory
from flask import Flask, jsonify, request, Response
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate
from langchain.vectorstores import ElasticsearchStore
from queue import Queue
from uuid import uuid4
import json
import os
import threading

INDEX = "workplace-app-docs"
INDEX_CHAT_HISTORY = "workplace-app-docs-chat-history"
ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

POISON_MESSAGE = "~~~END~~~"
SESSION_ID_TAG = "[SESSION_ID]"
SOURCE_TAG = "[SOURCE]"
DONE_TAG = "[DONE]"


class QueueCallbackHandler(BaseCallbackHandler):
    def __init__(
        self,
        queue: Queue,
    ):
        self.queue = queue
        self.in_human_prompt = True

    def on_retriever_end(self, documents, *, run_id, parent_run_id = None, **kwargs):
        if len(documents) > 0:
            for doc in documents:
                source = {
                    'name': doc.metadata['name'],
                    'page_content': doc.page_content
                }
                self.queue.put(f"{SOURCE_TAG} {json.dumps(source)}")
        
    def on_llm_new_token(self, token, **kwargs):
        if not self.in_human_prompt:
            self.queue.put(token)

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        self.in_human_prompt = prompts[0].startswith('Human:')

    def on_llm_end(self, response, *, run_id, parent_run_id = None, **kwargs):
        if not self.in_human_prompt:
            self.queue.put(POISON_MESSAGE)


elasticsearch_client = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID,
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)

store = ElasticsearchStore(
    es_connection=elasticsearch_client,
    index_name=INDEX,
    strategy=ElasticsearchStore.SparseVectorRetrievalStrategy()
)

retriever = store.as_retriever()

llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    streaming=True,
    temperature=0.2
)

general_system_template = """ 
Use the following pieces of context to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
----
{context}
----
"""
general_user_template = "Question: {question}"
qa_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(general_system_template),
    HumanMessagePromptTemplate.from_template(general_user_template)
])

chat = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=store.as_retriever(),
    return_source_documents=True,
    combine_docs_chain_kwargs={'prompt': qa_prompt},
    # verbose=True
)

stream_queue = Queue()

app = Flask(__name__, static_folder="../frontend/public")


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
    request_json = request.get_json()
    question = request_json.get("question")
    if question is None:
        return jsonify({"msg": "Missing question from request JSON"}), 400

    session_id = request.args.get('session_id', str(uuid4()))
    
    print('Chat session ID: ', session_id)
    chat_history = ElasticsearchChatMessageHistory(
        client=elasticsearch_client,
        index=INDEX_CHAT_HISTORY,
        session_id=session_id
    )

    def generate(queue: Queue):
        yield f"data: {SESSION_ID_TAG} {session_id}\n\n"

        message = None
        while True:
            message = queue.get()

            if message == POISON_MESSAGE: # Poison message 
                break

            yield f"data: {message}\n\n"

        yield f"data: {DONE_TAG}\n\n"

    threading.Thread(
        target=ask_question,
        args=(question, stream_queue, chat_history)
    ).start()

    return Response(generate(stream_queue), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(port=4000, debug=True)
