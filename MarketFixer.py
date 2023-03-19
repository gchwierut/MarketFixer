import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Define client ID, client secret, and redirect URI
client_id = "yourclientid"
client_secret = "yourclientsecret"
redirect_uri = "yourredirecturi"

# Define the scope of the permissions needed
scope = "playlist-modify-private playlist-modify-public user-read-private user-read-email playlist-read-private"

# Create Spotipy client object using the SpotifyOAuth authentication manager
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

# Get the user's playlists
offset = 0
playlists = []
while True:
    results = sp.current_user_playlists(offset=offset)
    playlists += results["items"]
    if results["next"] is None:
        break
    offset += len(results["items"])

# Print out the user's playlists
print("Your playlists:")
for i, playlist in enumerate(playlists):
    print(f"{i+1}. {playlist['name']}")

# Ask the user to choose a playlist
playlist_choice = input("Enter the number of the playlist you want to modify: ")

# Get the ID of the chosen playlist
playlist_id = playlists[int(playlist_choice)-1]["id"]

# Use Spotipy client to get the user's country
user_country = sp.current_user()["country"]

# Use Spotipy client to get all the tracks in the playlist
playlist_tracks = []
offset = 0
while True:
    results = sp.playlist_items(playlist_id, offset=offset)
    playlist_tracks += results["items"]
    if results["next"] is None:
        break
    offset += len(results["items"])

# Check if the last track index file exists, and create it if it doesn't
if not os.path.exists("last_track_index.txt"):
    with open("last_track_index.txt", "w") as f:
        f.write("0")
# Load the last processed track index from a file
with open("last_track_index.txt", "r") as f:
    last_processed_track_index = int(f.read())

# Loop through each track in the playlist, starting from the last processed track index
for i in range(last_processed_track_index, len(playlist_tracks)):
    track = playlist_tracks[i]
    track_name = track["track"]["name"]
    artist_name = track["track"]["artists"][0]["name"]
    track_id = track["track"]["id"]
    
    # Check if track is available in user's country
    track_info = sp.track(track_id)
    available_markets = track_info["available_markets"]
    if user_country not in available_markets:
        # Search for a replacement track by the same artist
        query = f'artist:{artist_name} track:{track_name.split(" - ")[0]}'
        results = sp.search(query, limit=1, type='track')

        # Check if a replacement track was found
        if len(results["tracks"]["items"]) > 0:
            replacement_track_id = results["tracks"]["items"][0]["id"]

            # Replace the unavailable track with the replacement track at the same index
            sp.playlist_remove_specific_occurrences_of_items(playlist_id, [{ "uri": track["track"]["uri"], "positions": [i] }])
            sp.playlist_add_items(playlist_id, [replacement_track_id], position=i)

            # Print a message indicating that the track has been replaced
            print(f"Track '{track_name}' by '{artist_name}' has been replaced with '{results['tracks']['items'][0]['name']}'")

        else:
            # Print a message indicating that no replacement was found
            print(f"No replacement track found for '{track_name}' by '{artist_name}'")
    else:
        # Print a message indicating that the track is available
        print(f"Track '{track_name}' by '{artist_name}' is available in your country")

    # Save the current track index to a file
    with open("last_track_index.txt", "w") as f:
        f.write(str(i))

