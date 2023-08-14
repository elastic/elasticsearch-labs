import json
import logging
from typing import List
from elasticsearch import ApiError, Elasticsearch

from langchain.schema import BaseChatMessageHistory
from langchain.schema.messages import BaseMessage, _message_to_dict, messages_from_dict

logger = logging.getLogger(__name__)

class ElasticsearchChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores history in Elasticsearch.

    Args:
        client: Elasticsearch client.
        index: name of the index to use.
        session_id: arbitrary key that is used to store the messages
            of a single chat session.
    """

    def __init__(
        self,
        client: Elasticsearch,
        index: str,
        session_id: str,
    ):
        self.client: Elasticsearch = client
        self.index: str = index
        self.session_id: str = session_id

        if not client.indices.exists(index=index):
            client.indices.create(
                index=index,
                mappings={
                    "properties": {
                        "session_id": {"type": "keyword"},
                        "history": {"type": "text"}
                    }
                }
            )

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve the messages from Elasticsearch"""
        try:
            result = self.client.search(
                index=self.index,
                query={"term": {"session_id": self.session_id}}
            )
        except ApiError as err:
            logger.error(err)

        if result and len(result["hits"]["hits"]) > 0:
            items = [json.loads(document["_source"]["history"]) for document in result["hits"]["hits"]]
        else:
            items = []

        return messages_from_dict(items)

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the chat session in Elasticsearch"""
        try:
            self.client.index(
                index=self.index,
                body={
                    "session_id": self.session_id,
                    "history": json.dumps(_message_to_dict(message))
                }
            )
        except ApiError as err:
            logger.error(err)

    def clear(self) -> None:
        """Clear session memory in Elasticsearch"""
        try:
            self.client.delete_by_query(
                index=self.index,
                query={"term": {"session_id": self.session_id}}
            )
        except ApiError as err:
            logger.error(err)
