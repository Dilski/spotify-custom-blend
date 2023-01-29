# spotify-custom-blend

Spotify creates a Blend playlist for 2 people, with a mix of songs they've been listening to recently.

My partner and I have a good crossover in music taste, but she doesn't like Hyperpop (such as [100 Gecs](https://youtu.be/1Bw2dTY3SsQ)).

This python code used the `spotipy` wrapper around the Spotify API to:

1. Get the tracks from our Blend playlist
2. Get all of the artists from all tracks on a special "Blocks" Playlist
3. Creates or updates a playlist containing the tracks on our Blend playlist that don't have artists in the "Blocks" playlist.

This code is designed to run in AWS Lambda on a daily schedule, caching credentials as a secure string in SSM Parameter Store.
