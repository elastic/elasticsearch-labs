from langchain_elasticsearch import ElasticsearchStore, DenseVectorStrategy, SparseVectorStrategy
from llm_integrations import get_llm
from elasticsearch_client import (
    elasticsearch_client,
    get_elasticsearch_chat_message_history,
)
from flask import render_template, stream_with_context, current_app
import json
import os

INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
INDEX_CHAT_HISTORY = os.getenv(
    "ES_INDEX_CHAT_HISTORY", "workplace-app-docs-chat-history"
)
MODEL_ID = os.getenv("ES_MODEL_ID", ".elser_model_2")
STRATEGY_TYPE = os.getenv("ES_STRATEGY_TYPE", "sparse")
VECTOR_FIELD = os.getenv("ES_VECTOR_FIELD", "vector")
QUERY_FIELD = os.getenv("ES_QUERY_FIELD", "text")

SESSION_ID_TAG = "[SESSION_ID]"
SOURCE_TAG = "[SOURCE]"
DONE_TAG = "[DONE]"

if STRATEGY_TYPE == "sparse":
    strategy = SparseVectorStrategy(model_id=MODEL_ID)
    store = ElasticsearchStore(
        es_connection=elasticsearch_client,
        index_name=INDEX,
        strategy=strategy,
    )
elif STRATEGY_TYPE == "dense":
    strategy = DenseVectorStrategy(model_id=MODEL_ID, hybrid=True)
    store = ElasticsearchStore(
        es_connection=elasticsearch_client,
        index_name=INDEX,
        vector_query_field=VECTOR_FIELD,
        query_field=QUERY_FIELD,
        strategy=strategy,
    )
else:
    raise ValueError(f"Invalid strategy type: {STRATEGY_TYPE}")


@stream_with_context
def ask_question(question, session_id):
    yield f"data: {SESSION_ID_TAG} {session_id}\n\n"
    current_app.logger.debug("Chat session ID: %s", session_id)

    chat_history = get_elasticsearch_chat_message_history(
        INDEX_CHAT_HISTORY, session_id
    )

    if len(chat_history.messages) > 0:
        # create a condensed question
        condense_question_prompt = render_template(
            "condense_question_prompt.txt",
            question=question,
            chat_history=chat_history.messages,
        )
        condensed_question = get_llm().invoke(condense_question_prompt).content
    else:
        condensed_question = question

    current_app.logger.debug("Condensed question: %s", condensed_question)
    current_app.logger.debug("Question: %s", question)

    docs = store.as_retriever().invoke(condensed_question)
    for doc in docs:
        doc_source = {**doc.metadata, "page_content": doc.page_content}
        if "name" in doc.metadata:
            current_app.logger.debug(
                "Retrieved document passage from: %s", doc.metadata["name"]
            )
        yield f"data: {SOURCE_TAG} {json.dumps(doc_source)}\n\n"

    qa_prompt = render_template(
        "rag_prompt.txt",
        question=question,
        docs=docs,
        chat_history=chat_history.messages,
    )

    answer = ""
    for chunk in get_llm().stream(qa_prompt):
        content = chunk.content.replace(
            "\n", " "
        )  # the stream can get messed up with newlines
        yield f"data: {content}\n\n"
        answer += chunk.content

    yield f"data: {DONE_TAG}\n\n"
    current_app.logger.debug("Answer: %s", answer)

    chat_history.add_user_message(question)
    chat_history.add_ai_message(answer)
