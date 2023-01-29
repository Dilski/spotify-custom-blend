import os

import spotipy
import boto3
from spotipy.oauth2 import SpotifyOAuth

from spotipy_ssm_credentials_cache import SSMCacheHandler
from custom_spotify_blend_creator import CustomSpotifyBlendCreator

ssm_client = boto3.client("ssm")


def lambda_handler(event, context):
    client = CustomSpotifyBlendCreator(
        spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=ssm_client.get_parameter(Name="/spotify/client_id")[
                    "Parameter"
                ]["Value"],
                client_secret=ssm_client.get_parameter(
                    Name="/spotify/client_secret", WithDecryption=True
                )["Parameter"]["Value"],
                redirect_uri=ssm_client.get_parameter(Name="/spotify/redirect_url")[
                    "Parameter"
                ]["Value"],
                scope=[
                    "playlist-modify-private",
                    "playlist-modify-public",
                    "playlist-read-private",
                ],
                cache_handler=SSMCacheHandler("/spotify/credcache"),
            ),
        ),
        blend_playlist_id=ssm_client.get_parameter(Name="/spotify/blend_playlist_id")[
            "Parameter"
        ]["Value"],
        banned_playlist_id=ssm_client.get_parameter(Name="/spotify/banned_playlist_id")[
            "Parameter"
        ]["Value"],
        destination_playlist_id=ssm_client.get_parameter(
            Name="/spotify/destination_playlist_id"
        )["Parameter"]["Value"],
    )
    playlist = client.create_modified_blend()
    return {"playlistUrl": f"https://open.spotify.com/playlist/{playlist}"}
