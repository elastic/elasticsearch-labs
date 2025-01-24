from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SpotifyTrack:
    """A class representing a Spotify track with its metadata and listening context.

    Attributes:
        id (str): The unique identifier of the track.
        album (str): The name of the album containing the track.
        artist (list[str]): List of artist names associated with the track.
        country (str): The country where the track was played.
        dayOfWeek (str): The day of the week when the track was played.
        duration (int): Duration of the track in milliseconds.
        explicit (bool): Whether the track has explicit content.
        hourOfDay (int): The hour of the day when the track was played (0-23).
        listened_to (float, optional): The duration listened to in milliseconds. Defaults to None.
        ip (str): The IP address of the device that played the track.
        offline (bool): Whether the track was played in offline mode.
        reason_start (str): The reason why the track started playing.
        reason_end (str): The reason why the track stopped playing.
        platform (str): The platform used to play the track.
        played_at (datetime): The timestamp when the track was played.
        skipped (bool): Whether the track was skipped.
        title (str): The title of the track.
        url (str): The Spotify URL of the track.
        user (str): The user who played the track.
        user_agent (str): The user agent string of the device used to play the track.
    """

    id: str
    album: str
    artist: list[str]
    country: str
    dayOfWeek: str
    duration: int
    explicit: bool
    hourOfDay: int
    listened_to_ms: int
    offline: bool
    reason_start: str
    reason_end: str
    platform: str
    played_at: datetime
    shuffle: bool
    skipped: bool
    title: str
    url: str
    user: Optional[str] = None
    listened_to_pct: Optional[float] = None
    ip: Optional[str] = None
    spotify_metadata: Optional[dict] = None
