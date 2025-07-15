import json
import os
from datetime import datetime
from getpass import getpass
from typing import Dict, List

import uvicorn
from elasticsearch import Elasticsearch
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Elasticsearch - FastAPI with websockets")


os.environ["ELASTICSEARCH_ENDPOINT"] = getpass(
    "Insert the Elasticsearch endpoint here: "
)
os.environ["ELASTICSEARCH_API_KEY"] = getpass("Insert the Elasticsearch API key here: ")

es_client = Elasticsearch(
    hosts=[os.environ["ELASTICSEARCH_ENDPOINT"]],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

PRODUCTS_INDEX = "products"


class Product(BaseModel):
    product_name: str
    price: float
    description: str


class SearchNotification(BaseModel):
    session_id: str
    query: str
    results_count: int
    timestamp: datetime = Field(default_factory=datetime.now)


class SearchResponse(BaseModel):
    query: str
    results: List[Dict]
    total: int


# Store active WebSocket connections
connections: List[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    print(f"Client connected. Total connections: {len(connections)}")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(connections)}")


@app.get("/search")
async def search_products(q: str, session_id: str = "unknown"):
    # List of product names that should trigger a notification
    NOTIFY_PRODUCTS = ["iPhone 15 Pro", "Kindle Paperwhite"]

    try:
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"product_name": q}},
                        {"match_phrase": {"description": q}},
                    ],
                    "minimum_should_match": 1,
                }
            },
            "size": 20,
        }

        response = es_client.search(index=PRODUCTS_INDEX, body=query)

        results = []
        notify_found = False

        for hit in response["hits"]["hits"]:
            product = hit["_source"]
            product["score"] = hit["_score"]
            results.append(product)

            # Check if this product should trigger a notification
            if product.get("product_name") in NOTIFY_PRODUCTS:
                notify_found = True

        results_count = response["hits"]["total"]["value"]

        if notify_found:
            notification = SearchNotification(
                session_id=session_id, query=q, results_count=results_count
            )

            for connection in connections.copy():
                try:
                    await connection.send_text(
                        json.dumps(
                            {
                                "type": "search",
                                "session_id": session_id,
                                "query": q,
                                "results_count": results_count,
                                "timestamp": notification.timestamp.isoformat(),
                            }
                        )
                    )
                except:
                    connections.remove(connection)

        return SearchResponse(query=q, results=results, total=results_count)

    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        return HTTPException(status_code=status_code, detail=str(e))


@app.get("/")
async def get_main_page():
    return FileResponse("index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
