import logging
from pathlib import Path
import typer
from datetime import datetime
import json
from rich.logging import RichHandler
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
)
from services import SpotifyService, ElasticsearchService
from models import SpotifyTrack

logger = None


def try_parsing_date(text):
    """Attempt to parse a date"""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            logger.error(f"Error parsing date: {text}")
            pass


def process_history_file(
    file_path: str,
    spotify_svc: SpotifyService,
    es_svc: ElasticsearchService,
    user_name: str,
):
    """Main processing function"""
    # Set up rich logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    logger = logging.getLogger(__name__)
    console = Console()

    with open(file_path) as f:
        history = json.load(f)

    console.print(f"[green]Processing {file_path}")

    documents = []
    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Processing tracks...", total=len(history))

        total_entries = len(history)
        batch_size = 50
        for i in range(0, total_entries, batch_size):
            entries_batch = history[i : i + batch_size]
            metadata_batch = spotify_svc.get_tracks_metadata(entries_batch)
            for entry in entries_batch:
                try:
                    # let's make sure to only look at songs
                    # we do not support videos, podcats or
                    # anything else yet.
                    if entry["spotify_track_uri"] is not None and entry[
                        "spotify_track_uri"
                    ].startswith("spotify:track:"):
                        track_id = entry["spotify_track_uri"].replace(
                            "spotify:track:", ""
                        )
                        metadata = metadata_batch.get(track_id, None)
                        played_at = try_parsing_date(entry["ts"])
                        if metadata is not None:
                            documents.append(
                                SpotifyTrack(
                                    id=str(
                                        int(
                                            (
                                                played_at - datetime(1970, 1, 1)
                                            ).total_seconds()
                                        )
                                    )
                                    + "_"
                                    + entry["master_metadata_album_artist_name"],
                                    artist=[
                                        artist["name"] for artist in metadata["artists"]
                                    ],
                                    album=metadata["album"]["name"],
                                    country=entry["conn_country"],
                                    duration=metadata["duration_ms"],
                                    explicit=metadata["explicit"],
                                    listened_to_pct=(
                                        entry["ms_played"] / metadata["duration_ms"]
                                        if metadata["duration_ms"] > 0
                                        else None
                                    ),
                                    listened_to_ms=entry["ms_played"],
                                    ip=entry["ip_addr"],
                                    reason_start=entry["reason_start"],
                                    reason_end=entry["reason_end"],
                                    shuffle=entry["shuffle"],
                                    skipped=entry["skipped"],
                                    offline=entry["offline"],
                                    title=metadata["name"],
                                    platform=entry["platform"],
                                    played_at=played_at,
                                    spotify_metadata=metadata,
                                    hourOfDay=played_at.hour,
                                    dayOfWeek=played_at.strftime("%A"),
                                    url=metadata["external_urls"]["spotify"],
                                    user=user_name,
                                )
                            )
                        else:
                            console.print(f"[red]Metadata not found for track: {entry}")
                        if len(documents) >= 500:
                            console.print(
                                f"[green]Indexing batch of tracks... {len(documents)}"
                            )
                            es_svc.bulk_index(documents)
                            documents = []
                        progress.advance(task)

                except Exception as e:
                    logger.error(f"Error processing track: {e}")
                    spotify_svc.metadata_cache.save_cache()
                    raise

    if documents:
        console.print(f"[green]Indexing final batch of tracks... {len(documents)}")
        es_svc.bulk_index(documents)
        console.print(f"[green]Done! {file_path} processed!")

    spotify_svc.metadata_cache.save_cache()


app = typer.Typer()


@app.command()
def process_history(
    es_url: str = typer.Option(..., help="Elasticsearch URL"),
    es_api_key: str = typer.Option(..., help="Elasticsearch API Key"),
    spotify_client_id: str = typer.Option(None, help="Spotify Client ID"),
    spotify_client_secret: str = typer.Option(None, help="Spotify Client Secret"),
    user_name: str = typer.Option(None, help="User name"),
):
    """Setup the services"""
    if spotify_client_id and spotify_client_secret:
        spotify_svc = SpotifyService(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri="http://localhost:9100",
        )
    es_svc = ElasticsearchService(es_url=es_url, api_key=es_api_key)
    # Ensure index exists
    es_svc.check_index()
    es_svc.check_pipeline()

    files = list(Path("to_read").glob("*Audio*.json"))
    if not files:
        raise ValueError(
            "No JSON files found in 'to_read' directory, expected them to be named *Audio*.json, like Streaming_History_Audio_2023_8.json"
        )
    else:
        for file_path in files:
            process_history_file(file_path, spotify_svc, es_svc, user_name)
            move_file(file_path)


def move_file(file_path: Path):
    """Move the file to the 'processed' directory"""
    processed_dir = Path("processed")
    processed_dir.mkdir(exist_ok=True)
    new_path = Path("processed") / file_path.name
    file_path.rename(new_path)


if __name__ == "__main__":
    app()
