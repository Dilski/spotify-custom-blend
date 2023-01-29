import os
from datetime import datetime
from typing import Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .spotipy_ssm_credentials_cache import SSMCacheHandler


class CustomSpotifyBlendCreator:
    def __init__(
        self,
        sp: spotipy.Spotify,
        blend_playlist_id: str,
        banned_playlist_id: str,
        destination_playlist_id: Optional[str] = None,
    ) -> None:
        self.sp = sp
        self.user_id = sp.me()["id"]
        self.blend_playlist_id = blend_playlist_id
        self.banned_playlist_id = banned_playlist_id
        self.destination_playlist_id = destination_playlist_id

    @staticmethod
    def _extract_artist_ids_for_track(track: dict) -> list[str]:
        return [artist["id"] for artist in track["artists"]]

    def _get_banned_artist_ids(self) -> list[str]:
        banned_playlist_items = self.sp.playlist_tracks(self.banned_playlist_id)[
            "items"
        ]
        banned_artists = [
            artist_id
            for item in banned_playlist_items
            for artist_id in self._extract_artist_ids_for_track(item["track"])
        ]
        return banned_artists

    def _create_playlist_with_tracks(self, tracks: list[str]) -> dict:
        if self.destination_playlist_id is None:
            playlist_id = self.sp.user_playlist_create(
                self.user_id,
                f"modified-blend-{datetime.now().timestamp()}",
                public=False,
                collaborative=True,
            )["id"]
        else:
            playlist_id = self.destination_playlist_id

        self.sp.playlist_replace_items(playlist_id, tracks)
        self.sp.playlist_change_details(
            playlist_id=playlist_id,
            description=(
                "Custom Blend for Eilidh & Dillon. "
                f"Last updated: {datetime.now().isoformat(timespec='minutes', sep=' ')}"
            ),
        )
        return playlist_id

    def create_modified_blend(self):
        playlist_items = self.sp.playlist_tracks(self.blend_playlist_id)["items"]

        banned_artists = self._get_banned_artist_ids()

        new_playlist = [
            item["track"]["uri"]
            for item in playlist_items
            if all(
                artist not in banned_artists
                for artist in self._extract_artist_ids_for_track(item["track"])
            )
        ]
        return self._create_playlist_with_tracks(new_playlist)


def lambda_handler(event, context):
    client = CustomSpotifyBlendCreator(
        spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                scope=[
                    "playlist-modify-private",
                    "playlist-modify-public",
                    "playlist-read-private",
                ],
                cache_handler=SSMCacheHandler("/spotify/credcache"),
            ),
        ),
        blend_playlist_id=os.getenv("BLEND_PLAYLIST_ID"),
        banned_playlist_id=os.getenv("BANNED_PLAYLIST_ID"),
        destination_playlist_id=os.getenv("DISTINATION_PLAYLIST_ID"),
    )
    playlist = client.create_modified_blend()
    return {"playlistUrl": f"https://open.spotify.com/playlist/{playlist}"}
