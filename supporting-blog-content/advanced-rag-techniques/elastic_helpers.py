import logging
from typing import Optional, Tuple, List, Dict, Any
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import bulk
import json
import re 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ESConnector:

    def __init__(self, hosts: List[str], credentials: Optional[Tuple[str, str]] = None, use_ssl: bool = True):
        """
        Initialize the ESConnector.

        Args:
            hosts (List[str]): A list of Elasticsearch host URLs.
            credentials (Optional[Tuple[str, str]]): A tuple containing the username and password for authentication.
            use_ssl (bool): Whether to use SSL for the connection. Defaults to True.

        """
        self.hosts = hosts
        self.credentials = credentials
        self.use_ssl = use_ssl
        self.conn = self.create_es_connection()

    def create_es_connection(self) -> Elasticsearch:
        """
        Create a connection to the Elasticsearch cluster.

        Returns:
            Elasticsearch: An Elasticsearch client instance.
        """
        if self.credentials:
            username, password = self.credentials
            es = Elasticsearch(
                hosts=self.hosts,
                basic_auth=(username, password),
                # use_ssl=self.use_ssl,
                verify_certs=True
            )
        else:
            es = Elasticsearch(
                hosts=self.hosts,
                # use_ssl=self.use_ssl,
                verify_certs=True
            )
        
        logger.info(f"Connection created for hosts: {self.hosts}")
        return es


    def ping(self) -> None:
        if self.conn.ping():
            print("Ping successful: Connected to Elasticsearch!")
        else:
            print("Ping unsuccessful: Elasticsearch is not available!")

    def print_indices(self) -> None:
        indices = self.conn.indices.get_alias(index="*")
        for index in indices:
            print(index)

    def get_cluster_health(self, printOnly=False) -> dict[str, Any]:
        """
        Get the health status of the cluster.

        Returns:
            dict: The health status of the cluster.
        """
        try:
            health = self.conn.cluster.health()
            logger.info(f"Cluster health retrieved successfully: \n\n {str(health)}")
            if not printOnly:
                return health
        except Exception as e:
            logger.error(f"An error occurred while retrieving cluster health: {e}")
            return {}

    def get_index_settings(self, index_name: str) -> dict[str, Any]:
        """
        Get the settings of an index.

        Args:
            index_name (str): The name of the index.

        Returns:
            dict: The settings of the index.
        """
        try:
            settings = self.conn.indices.get_settings(index=index_name)
            logger.info(f"Settings for index {index_name} retrieved successfully.")
            return settings
        except NotFoundError:
            logger.warning(f"Index {index_name} not found.")
            return {}
        except Exception as e:
            logger.error(f"An error occurred while retrieving settings for index {index_name}: {e}")
            return {}

    def update_index_settings(self, index_name: str, new_settings: dict[str, Any]) -> None:
        """
        Update the settings of an index.

        Args:
            index_name (str): The name of the index.
            new_settings (dict): The new settings to apply to the index.
        """
        try:
            self.conn.indices.put_settings(index=index_name, settings=new_settings)
            logger.info(f"Settings for index {index_name} updated successfully.")
        except NotFoundError:
            logger.warning(f"Index {index_name} not found.")
        except Exception as e:
            logger.error(f"An error occurred while updating settings for index {index_name}: {e}")

    def check_index_existence(self, index_name) -> bool:
        return self.conn.indices.exists(index=index_name)

    def create_es_index(self, es_configuration: dict, index_name: str, override=True) -> None:
        """
        Create a new index with the specified configuration.

        Args:
            es_configuration (dict): The configuration for the index, including settings and mappings.
            index_name (str): The name of the new index.
        """
        try:
            if override:
                self.delete_es_index(index_name=index_name)

            self.conn.indices.create(
                index=index_name,
                settings=es_configuration.get("settings", {}),
                mappings=es_configuration.get("mappings", {})
            )
            logger.info(f"New index {index_name} created!")
        except Exception as e:
            logger.error(f"An error occurred while creating the index {index_name}: {e}")

    def delete_es_index(self, index_name: str) -> None:
        """
        Delete an index if it exists.

        Args:
            index_name (str): The name of the index to delete.
        """
        try:
            if self.conn.indices.exists(index=index_name):
                logger.info(f"The index {index_name} already exists, going to remove it")
                self.conn.indices.delete(index=index_name)
                logger.info(f"Index {index_name} deleted successfully.")
            else:
                logger.info(f"Index {index_name} does not exist.")
        except NotFoundError:
            logger.warning(f"Index {index_name} not found. Nothing to delete.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

class ESIndexer(ESConnector):

    def __init__(self, cloud_id: str, credentials: Optional[Tuple[str, str]] = None):
        super().__init__(cloud_id, credentials)

    def add_document(self, index_name: str, document: dict[str, Any], doc_id: Optional[str] = None) -> None:
        """
        Add a document to an index.

        Args:
            index_name (str): The name of the index.
            document (dict): The document to add.
            doc_id (Optional[str]): The ID of the document. If None, Elasticsearch will generate one.

        """
        try:
            if doc_id:
                self.conn.index(index=index_name, id=doc_id, document=document)
            else:
                self.conn.index(index=index_name, document=document)
            logger.info(f"Document added to {index_name}")
        except Exception as e:
            logger.error(f"An error occurred while adding the document to {index_name}: {e}")

    def delete_document(self, index_name: str, doc_id: str) -> None:
        """
        Delete a document from an index.

        Args:
            index_name (str): The name of the index.
            doc_id (str): The ID of the document to delete.
        """
        try:
            self.conn.delete(index=index_name, id=doc_id)
            logger.info(f"Document with ID {doc_id} deleted from {index_name}")
        except NotFoundError:
            logger.warning(f"Document with ID {doc_id} not found in index {index_name}.")
        except Exception as e:
            logger.error(f"An error occurred while deleting the document from {index_name}: {e}")

    def get_document(self, index_name: str, doc_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve a document by its ID from an index.

        Args:
            index_name (str): The name of the index.
            doc_id (str): The ID of the document to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The retrieved document, or None if not found.
        """
        try:
            response = self.conn.get(index=index_name, id=doc_id)
            logger.info(f"Document with ID {doc_id} retrieved from {index_name}")
            return response["_source"]
        except NotFoundError:
            logger.warning(f"Document with ID {doc_id} not found in index {index_name}.")
            return None
        except Exception as e:
            logger.error(f"An error occurred while retrieving the document from {index_name}: {e}")
            return None

    def update_document(self, index_name: str, doc_id: str, updated_fields: dict[str, Any]) -> None:
        """
        Update a document in an index.

        Args:
            index_name (str): The name of the index.
            doc_id (str): The ID of the document to update.
            updated_fields (dict): The fields to update in the document.
        """
        try:
            self.conn.update(index=index_name, id=doc_id, doc=updated_fields)
            logger.info(f"Document with ID {doc_id} updated in {index_name}")
        except NotFoundError:
            logger.warning(f"Document with ID {doc_id} not found in index {index_name}.")
        except Exception as e:
            logger.error(f"An error occurred while updating the document in {index_name}: {e}")


class ESBulkIndexer(ESIndexer):

    def __init__(self, cloud_id: str, credentials: Optional[Tuple[str, str]] = None):
        super().__init__(cloud_id, credentials)

    def bulk_upload_documents(self, index_name: str, documents: list[dict[str, Any]], id_col: str, batch_size: int = 1000) -> int:
        """
        Bulk upload documents to an Elasticsearch index with batching.

        Args:
            index_name (str): The name of the index.
            documents (list[dict[str, Any]]): The list of documents to upload.
            id_col (str): The name of the column to use as the document ID.
            batch_size (int): The number of documents to upload in each batch. Default is 1000.

        Returns:
            int: The total number of successfully indexed documents.
        """
        total_success = 0
        total_failed = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            actions = [
                {
                    "_op_type": "update",
                    "_index": index_name,
                    "_id": document[id_col],
                    "doc": document,
                    "doc_as_upsert": True
                }
                for document in batch
            ]

            try:
                success, failed = bulk(self.conn, actions)
                total_success += success
                total_failed += len(failed)
                logger.info(f"Batch {i//batch_size + 1}: Successfully indexed {success} documents to {index_name}")
                if failed:
                    logger.warning(f"Batch {i//batch_size + 1}: Failed to index {len(failed)} documents")
            except Exception as e:
                logger.error(f"An error occurred while uploading batch {i//batch_size + 1} to {index_name}: {e}")

        logger.info(f"Total documents successfully indexed to {index_name}: {total_success}")
        if total_failed:
            logger.warning(f"Total documents failed to index: {total_failed}")

        return total_success
        

    def bulk_delete_documents(self, index_name: str, document_ids: list[str]) -> int:
        """
        Bulk delete documents from an Elasticsearch index.

        Args:
            index_name (str): The name of the index.
            document_ids (list[str]): The list of document IDs to delete.

        Returns:
            int: The number of successfully deleted documents.
        """
        actions = [
            {
                "_op_type": "delete",
                "_index": index_name,
                "_id": doc_id
            }
            for doc_id in document_ids
        ]

        try:
            success, failed = bulk(self.conn, actions)
            logger.info(f"Successfully deleted {success} documents from {index_name}")
            if failed:
                logger.warning(f"Failed to delete {len(failed)} documents")
            return success
        except Exception as e:
            logger.error(f"An error occurred while bulk deleting documents from {index_name}: {e}")
            return 0

    def bulk_reindex(self, source_index: str, target_index: str) -> dict:
        """
        Bulk reindex documents from one Elasticsearch index to another.

        Args:
            source_index (str): The name of the source index.
            target_index (str): The name of the target index.

        Returns:
            dict: The response from the reindex operation.
        """
        query = {
            "source": {"index": source_index},
            "dest": {"index": target_index}
        }

        try:
            response = self.conn.reindex(body=query, wait_for_completion=True)
            logger.info(f"Successfully reindexed documents from {source_index} to {target_index}")
            return response
        except Exception as e:
            logger.error(f"An error occurred while reindexing documents: {e}")
            return {}

class ESQueryMaker(ESConnector):

    def __init__(self, cloud_id: str, credentials: Optional[Tuple[str, str]] = None):
        super().__init__(cloud_id, credentials)

    def pretty_print_results(self, results: Dict) -> None:
        """
        Pretty print the search results.

        Args:
            results (Dict): The search results to print.
        """
        try:
            hits = results.get('hits', {}).get('hits', [])
            if not hits:
                print("No results found.")
                return

            for i, hit in enumerate(hits):
                print(f"\nResult {i + 1}:")
                source = hit.get('_source', {})
                print(json.dumps(source, indent=4))

        except Exception as e:
            print(f"Error in pretty printing results: {e}")


    def search_index(self, index_name: str, query: str, fields: List[str]) -> Dict:
        """
        Search for a query in a specific index over given fields.

        Args:
            index_name (str): The name of the index to search.
            query (str): The query string to search for.
            fields (List[str]): The list of fields to search over.

        Returns:
            Dict: The search results.
        """
        try:
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": fields
                    }
                }
            }
            response = self.conn.search(index=index_name, body=search_body)
            logger.info(f"Search executed on index: {index_name} with query: {query}")
            return response
        except Exception as e:
            logger.error(f"Error executing search on index: {index_name} with query: {query}. Error: {e}")
            raise e

    def parse_or_query(self, query_text: str, text_fields: List[str]) -> List[Dict]:
        # Split the query by 'OR', strip whitespace
        terms = [term.strip() for term in query_text.split(' OR ')]
        should_clauses = []
        for term in terms:
            # if len(term.split()) > 1:
            #     # If term has multiple words, use match_phrase
            #     for text_field in text_fields:
            #         should_clauses.append({"match": {text_field: term}})
            # else:
            #     # If term is a single word, use match
            for text_field in text_fields:
                should_clauses.append({"match": {text_field: term}})
        
        return should_clauses

    def hybrid_vector_search(self, index_name: str, query_text: str, query_vector: List[float], 
                            text_fields: List[str], vector_field: str, 
                            num_candidates: int = 100, num_results: int = 10) -> Dict:
        """
        Perform a hybrid search combining text and vector queries.

        Args:
            index_name (str): The name of the index to search.
            query_text (str): The text query string.
            query_vector (List[float]): The query vector for semantic search.
            text_field (str): The name of the text field to search.
            vector_field (str): The name of the dense vector field.
            num_candidates (int): Number of candidates to consider in the initial vector search.
            num_results (int): Number of final results to return.

        Returns:
            Dict: The search results.
        """
        try:
            # Parse the query_text and create the should clauses
            should_clauses = self.parse_or_query(query_text, text_fields)

            search_body = {
                "knn": {
                    "field": vector_field,
                    "query_vector": query_vector,
                    "k": num_candidates,
                    "num_candidates": num_candidates
                },
                "query": {
                    "bool": {
                        "must": [
                            {
                                "bool": {
                                    "should": should_clauses,
                                    "minimum_should_match": 1
                                }
                            }
                        ],
                        "should": [
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": """
                                        double vector_score = cosineSimilarity(params.query_vector, params.vector_field) + 1.0;
                                        double text_score = _score;
                                        return 0.7 * vector_score + 0.3 * text_score;
                                        """,
                                        "params": {
                                            "query_vector": query_vector,
                                            "vector_field": vector_field
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            response = self.conn.search(index=index_name, body=search_body, size=num_results)
            logger.info(f"Hybrid search executed on index: {index_name} with text query: {query_text}")
            return response, search_body
        except Exception as e:
            logger.error(f"Error executing hybrid search on index: {index_name}. Error: {e}")
            raise e