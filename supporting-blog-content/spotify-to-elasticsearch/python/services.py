from pathlib import Path
import json
from typing import Dict, List
from elasticsearch import Elasticsearch, helpers, exceptions
from rich.console import Console
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from models import SpotifyTrack

console = Console()


class MetadataCache:
    def __init__(self, cache_file: Path = Path("metadata_cache.json")):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        if self.cache_file.exists():
            return json.loads(self.cache_file.read_text())
        return {}

    def save_cache(self):
        console.print(f"[green] Saving cache to disk {len(self.cache)}")
        self.cache_file.write_text(json.dumps(self.cache))


class SpotifyService:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
            ),
            requests_timeout=30,
        )
        self.metadata_cache = MetadataCache()

    def get_tracks_metadata(self, track_ids: str) -> Dict:
        metadatas = {}
        to_fetch = []
        for track_id in track_ids:
            if track_id["spotify_track_uri"] is not None and track_id[
                "spotify_track_uri"
            ].startswith("spotify:track:"):
                track_id = track_id["spotify_track_uri"].replace("spotify:track:", "")
                if self.metadata_cache.cache.get(track_id, None) is not None:
                    metadatas[track_id] = self.metadata_cache.cache[track_id]
                else:
                    to_fetch.append(track_id)
        if len(to_fetch) > 0:
            spotify_answer = self.client.tracks(to_fetch)
            if spotify_answer["tracks"] is not None:
                # Spotify can be a bit annoying and send back an Array that has `None` in it.
                spotify_answer["tracks"] = [
                    t for t in spotify_answer["tracks"] if t is not None
                ]
                if len(to_fetch) != len(spotify_answer["tracks"]):
                    for missing_id in set(to_fetch) - {
                        t["id"] for t in spotify_answer["tracks"]
                    }:
                        console.print(
                            f"[red] Could not fetch metadata for track id: {missing_id}"
                        )
                if len(spotify_answer["tracks"]) > 0:
                    for track in spotify_answer["tracks"]:
                        metadatas[track["id"]] = track
                        self.metadata_cache.cache[track["id"]] = track
            else:
                console.print(
                    f"[red] Could not fetch metadata from Spotify. {to_fetch}"
                )
        return metadatas


class ElasticsearchService:
    def __init__(self, es_url: str, api_key: str, index: str = "spotify-history"):
        self.client = Elasticsearch(hosts=es_url, api_key=api_key, request_timeout=30)
        self.index = index

    def check_pipeline(self):
        pipeline = {"processors": [{"geoip": {"field": "ip", "ignore_failure": True}}]}
        try:
            self.client.ingest.put_pipeline(id="spotify", body=pipeline)
        except exceptions.RequestError as e:
            console.print(
                f"[red] Could not ingest the pipeline. Check permissions. {e}"
            )

    def check_index(self):
        if self.client.indices.exists(index=self.index).body is False:
            self.client.indices.create(
                index=self.index,
                settings={"final_pipeline": "spotify"},
                mappings={
                    "dynamic": "true",
                    "dynamic_date_formats": [
                        "strict_date_optional_time",
                        "yyyy/MM/dd HH:mm:ss Z||yyyy/MM/dd Z",
                    ],
                    "dynamic_templates": [
                        {
                            "stringsaskeywords": {
                                "match": "*",
                                "match_mapping_type": "string",
                                "mapping": {"type": "keyword"},
                            }
                        }
                    ],
                    "date_detection": True,
                    "numeric_detection": False,
                    "properties": {
                        "@timestamp": {
                            "type": "date",
                            "format": "strict_date_optional_time",
                        },
                        "album": {"type": "keyword"},
                        "artist": {"type": "keyword"},
                        "dayOfWeek": {"type": "keyword"},
                        "duration": {"type": "long"},
                        "explicit": {"type": "boolean"},
                        "geoip": {
                            "properties": {
                                "city_name": {"type": "keyword"},
                                "continent_name": {"type": "keyword"},
                                "country_iso_code": {"type": "keyword"},
                                "country_name": {"type": "keyword"},
                                "location": {"type": "geo_point"},
                                "region_iso_code": {"type": "keyword"},
                                "region_name": {"type": "keyword"},
                            }
                        },
                        "hourOfDay": {"type": "long"},
                        "ip": {"type": "ip"},
                        "not_found": {"type": "boolean"},
                        "offline": {"type": "boolean"},
                        "platform": {"type": "keyword"},
                        "played_at": {
                            "type": "date",
                            "format": "strict_date_optional_time",
                        },
                        "reason_end": {"type": "keyword"},
                        "reason_start": {"type": "keyword"},
                        "skipped": {"type": "boolean"},
                        "title": {"type": "keyword"},
                        "url": {"type": "keyword"},
                        "user": {"type": "keyword"},
                    },
                },
            )

    def bulk_index(self, documents: List[SpotifyTrack]):
        actions = [
            {
                "_index": self.index,
                "_id": doc.id,
                "_source": {**vars(doc), "@timestamp": doc.played_at},
            }
            for doc in documents
        ]
        return helpers.bulk(
            self.client,
            actions,
        )
