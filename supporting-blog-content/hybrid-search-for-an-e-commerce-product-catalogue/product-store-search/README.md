# Product Store Search

This project is an API that allows you to perform searches using both lexical and hybrid search,
integrating Elasticsearch as a search engine. In addition, the API offers the possibility of
applying filters to refine the results according to specific criteria.


## Prerequisites

- **Docker**: Make sure Docker is installed on your machine. You can install the latest version of
  Docker [here](https://docs.docker.com/get-docker/).
- **Docker Compose**: Docker Compose is automatically installed with Docker Desktop, but you can check the version and
  install it separately if needed [here](https://docs.docker.com/compose/install/).

## Features

- **Lexical Search**: Allows traditional keyword-based searches, where the results are matched exactly or partially based on the input terms.
- **Hybrid Search**: Combines both lexical and semantic search techniques to deliver more relevant and meaningful results.
- **Facets**: Enables the use of filters to narrow down the search results based on specific categories, such as product type, brand, or price range.
- **Pinned Results**: Allows promoting specific documents to the top of the search results to highlight important or featured content.

## Steps to Run

1. Clone this repository to your local machine (if you haven't done so already):
    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2. Navigate to the `docker` directory:
    ```bash
    cd docker
    ```

3. Run Docker Compose to start the services:
    ```bash
    docker-compose up
    ```

   This will download the required images, create, and start the containers defined in the `docker-compose.yml` file.

4. To run the containers in the background (detached mode), use the `-d` flag:
    ```bash
    docker-compose up -d
    ```

5. After starting the containers, you can view the logs with:
    ```bash
    docker-compose logs -f
    ```

6. To stop the containers, use the following command:
    ```bash
    docker-compose down
    ```

   This will stop and remove the containers created by Docker Compose.

## Create Index

   ```bash
    python infra/create_index.py
   ```

## Ingestion Data

   ```bash
    python ingestion/ingestion.py
   ```

## Run API

   ```bash
    python  api/api.py
   ```

### Endpoint Search

   ```bash
    curl --location 'http://127.0.0.1:5000/api/products/search?query=term'
   ```

### Endpoint Facets

   ```bash
    curl --location 'http://127.0.0.1:5000/api/products/facets?query=term'
   ```

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

