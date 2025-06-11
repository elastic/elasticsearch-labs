if __name__ == "__main__":

    import os
    import logging
    import json
    from dotenv import load_dotenv

    from elastic_client import es
    from elasticsearch import helpers

    from sentence_transformers import SentenceTransformer

    load_dotenv(override=True)

    INDEX_NAME = f"{os.environ.get('INDEX_NAME')}-local"

    # Delete the inded if it already exists
    es.indices.delete(index=f"{INDEX_NAME}", ignore_unavailable=True)

    # This function embeds the book descriptions using the sentence-transformers library locally
    # and saves the embedded descriptions to a new file.
    def embed_descriptions(
        file_path="../data/books.json", output_path="../data/books_embedded.json"
    ):

        model = SentenceTransformer("sentence-transformers/msmarco-MiniLM-L-12-v3")
        print("Model loaded for embedding...")

        with open(file_path, "r") as file:
            books = json.load(file)
        print(f"Loading books from file {file_path} for embedding...")

        book_descriptions = [book["book_description"] for book in books]
        embedded_books = []

        # Embed the book descriptions using the sentence-transformers model
        pool = model.start_multi_process_pool()

        print("Starting multi-process pool for embedding...")
        embedded_books = model.encode_multi_process(book_descriptions, pool)
        print("Embeddings computed. Shape:", embedded_books.shape)

        model.stop_multi_process_pool(pool)
        print("Stopping multi-process pool...")

        new_books = []

        for i, book in enumerate(books):
            # Add these lines before the error line
            book["description_embedding"] = embedded_books[i].tolist()
            new_books.append(book)
        print("Embeddings added to books.")

        # Write the embedded books to a new array of documents named books_embeded.json
        with open(output_path, "w") as file:
            file.write("[")
            for i, book in enumerate(new_books):
                json.dump(book, file)
                if i != len(new_books) - 1:
                    file.write(",")
            file.write("]")
        print(f"{len(new_books)} embedded books saved to file: {output_path}.")

    # This function creates the Elasticsearch index with the appropriate mappings.
    def create_books_index():
        # The description_embedding field is a dense vector field with 384 dimensions.
        mappings = {
            "mappings": {
                "properties": {
                    "book_title": {"type": "text"},
                    "author_name": {"type": "text"},
                    "rating_score": {"type": "float"},
                    "rating_votes": {"type": "integer"},
                    "review_number": {"type": "integer"},
                    "book_description": {"type": "text"},
                    "genres": {"type": "keyword"},
                    "year_published": {"type": "integer"},
                    "url": {"type": "text"},
                    "description_embedding": {"type": "dense_vector", "dims": 384},
                }
            }
        }

        es.indices.create(index=INDEX_NAME, body=mappings)
        print(f"Index '{INDEX_NAME}' created.")

    def create_one_book(book):

        try:
            resp = es.index(
                index=INDEX_NAME,
                id=book.get("id", None),
                body=book,
            )

            print(
                f'Successfully indexed book {book["book_title"]}! Result: {resp.get("result", None)}'
            )

        except Exception as e:
            print(f"Error occurred while indexing book: {e}")

    # This function ingests the books from the books_embedded.json file into the Elasticsearch index.
    def bulk_ingest_books(file_path="../data/books_embedded.json"):

        with open(file_path, "r") as file:
            books = json.load(file)

        # The actions list is used to bulk ingest the books into the Elasticsearch index.
        # Each action is a dictionary with the index name, document id, and source document.
        actions = [
            {"_index": INDEX_NAME, "_id": book.get("id", None), "_source": book}
            for book in books
        ]

        try:
            # Use the helpers.bulk() function to bulk ingest the books into the Elasticsearch index.
            #
            helpers.bulk(es, actions, chunk_size=1000)
            print(
                f"Successfully added {len(actions)} books into the '{INDEX_NAME}' index."
            )

        except helpers.BulkIndexError as e:
            print(f"Error occurred while ingesting books: {e}")

    # create the books index with the appropriate mappings
    create_books_index()

    # embed and index a small sample of books
    file_path = "../data/small_books.json"
    output_path = "../data/small_books_embedded.json"
    embed_descriptions(file_path, output_path)
    bulk_ingest_books(file_path)

    # Index a single book with embedding already created
    with open("../data/one_book_embedded.json", "r") as file:
        book = json.load(file)
        create_one_book(book)
