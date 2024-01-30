from flask import Flask, jsonify, request, Response, current_app
from flask_cors import CORS
from elasticsearch_client import elasticsearch_client
import os
import sys
import requests

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)


def get_identities_index(search_app_name):
    search_app = elasticsearch_client.search_application.get(
        name=search_app_name)
    identities_indices = elasticsearch_client.indices.get(
        index=".search-acl-filter*")
    secured_index = [
        app_index
        for app_index in search_app["indices"]
        if ".search-acl-filter-" + app_index in identities_indices
    ]
    if len(secured_index) > 0:
        identities_index = ".search-acl-filter-" + secured_index[0]
        return identities_index
    else:
        raise ValueError(
            "Could not find identities index for search application %s", search_app_name
        )


@app.route("/")
def api_index():
    return app.send_static_file("index.html")


@app.route("/api/default_settings", methods=["GET"])
def default_settings():
    return {
        "elasticsearch_endpoint": os.getenv("ELASTICSEARCH_URL") or "http://localhost:9200"
    }


@app.route("/api/search_proxy/<path:text>", methods=["POST"])
def search(text):
    response = requests.request(
        method="POST",
        url=os.getenv("ELASTICSEARCH_URL") + '/' + text,
        data=request.get_data(),
        allow_redirects=False,
        headers={"Authorization": request.headers.get(
            "Authorization"), "Content-Type": "application/json"}
    )

    return response.content


@app.route("/api/persona", methods=["GET"])
def personas():
    try:
        search_app_name = request.args.get("app_name")
        identities_index = get_identities_index(search_app_name)
        response = elasticsearch_client.search(
            index=identities_index, size=1000)
        hits = response["hits"]["hits"]
        personas = [x["_id"] for x in hits]
        personas.append("admin")
        return personas

    except Exception as e:
        current_app.logger.warn(
            "Encountered error %s while fetching personas, returning default persona", e
        )
        return ["admin"]


@app.route("/api/indices", methods=["GET"])
def indices():
    try:
        search_app_name = request.args.get("app_name")
        search_app = elasticsearch_client.search_application.get(
            name=search_app_name)
        return search_app['indices']

    except Exception as e:
        current_app.logger.warn(
            "Encountered error %s while fetching indices, returning no indices", e
        )
        return []


@app.route("/api/api_key", methods=["GET"])
def api_key():
    search_app_name = request.args.get("app_name")
    role_name = search_app_name + "-key-role"
    default_role_descriptor = {}
    default_role_descriptor[role_name] = {
        "cluster": [],
        "indices": [
            {
                "names": [search_app_name],
                "privileges": ["read"],
                "allow_restricted_indices": False,
            }
        ],
        "applications": [],
        "run_as": [],
        "metadata": {},
        "transient_metadata": {"enabled": True},
        "restriction": {"workflows": ["search_application_query"]},
    }
    identities_index = get_identities_index(search_app_name)
    try:
        persona = request.args.get("persona")
        if persona == "":
            raise ValueError("No persona specified")
        role_descriptor = {}

        if persona == "admin":
            role_descriptor = default_role_descriptor
        else:
            identity = elasticsearch_client.get(
                index=identities_index, id=persona)
            permissions = identity["_source"]["query"]["template"]["params"][
                "access_control"
            ]
            role_descriptor = {
                "dls-role": {
                    "cluster": ["all"],
                    "indices": [
                        {
                            "names": [search_app_name],
                            "privileges": ["read"],
                            "query": {
                                "template": {
                                    "params": {"access_control": permissions},
                                    "source": """{
                                        "bool": {
                                            "should": [
                                                {
                                                    "bool": {
                                                        "must_not": {
                                                            "exists": {
                                                                "field": "_allow_access_control"
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "terms": {
                                                        "_allow_access_control.enum": {{#toJson}}access_control{{/toJson}}
                                                    }
                                                }
                                            ]
                                        }
                                    }""",
                                }
                            },
                        }
                    ],
                    "restriction": {"workflows": ["search_application_query"]},
                }
            }
        api_key = elasticsearch_client.security.create_api_key(
            name=search_app_name+"-internal-knowledge-search-example-"+persona, expiration="1h", role_descriptors=role_descriptor)
        return {"api_key": api_key['encoded']}

    except Exception as e:
        current_app.logger.warn(
            "Encountered error %s while fetching api key", e)
        raise e


if __name__ == "__main__":
    app.run(port=3001, debug=True)
