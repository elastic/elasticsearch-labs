from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.prompts.prompt import PromptTemplate
from langchain.vectorstores import ElasticsearchStore
from queue import Queue
from llm_integrations import get_llm
from elasticsearch_client import (
    elasticsearch_client,
    get_elasticsearch_chat_message_history,
)
import json
import os

INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
INDEX_CHAT_HISTORY = os.getenv(
    "ES_INDEX_CHAT_HISTORY", "workplace-app-docs-chat-history"
)
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

    def on_retriever_end(self, documents, *, run_id, parent_run_id=None, **kwargs):
        if len(documents) > 0:
            for doc in documents:
                source = {
                    "name": doc.metadata["name"],
                    "page_content": doc.page_content,
                    "url": doc.metadata["url"],
                    "icon": doc.metadata["category"],
                    "updated_at": doc.metadata.get("updated_at", None),
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


store = ElasticsearchStore(
    es_connection=elasticsearch_client,
    index_name=INDEX,
    strategy=ElasticsearchStore.SparseVectorRetrievalStrategy(),
)

general_system_template = """
Human: Use the following passages to answer the user's question. 
Each passage has a SOURCE which is the title of the document. When answering, give the source name of the passages you are answering from, put them in a comma seperated list, prefixed at the start with SOURCES: $sources then print an empty line.

Example:

Question: What is the meaning of life?
Response:
The meaning of life is 42. \n

SOURCES: Hitchhiker's Guide to the Galaxy \n

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
    input_variables=["page_content", "name"],
    template="""
---
NAME: "{name}"
PASSAGE:
{page_content}
---
""",
)

retriever = store.as_retriever()
llm = get_llm()
chat = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=store.as_retriever(),
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": qa_prompt, "document_prompt": document_prompt},
    verbose=True,
)


def parse_stream_message(session_id, queue: Queue):
    yield f"data: {SESSION_ID_TAG} {session_id}\n\n"

    message = None
    break_out_flag = False
    while True:
        message = queue.get()
        for line in message.splitlines():
            if line == POISON_MESSAGE:
                break_out_flag = True
                break
            yield f"data: {line}\n\n"
        if break_out_flag:
            break

    yield f"data: {DONE_TAG}\n\n"


def ask_question(question, queue, session_id):
    chat_history = get_elasticsearch_chat_message_history(
        INDEX_CHAT_HISTORY, session_id
    )
    result = chat(
        {"question": question, "chat_history": chat_history.messages},
        callbacks=[QueueCallbackHandler(queue)],
    )

    chat_history.add_user_message(result["question"])
    chat_history.add_ai_message(result["answer"])
