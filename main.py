from spotifyClient import SpotifyClient

def run():
    client_id = "c49576a273214dc9b2a5b1227d34e4bd"
    # Create spotify client
    spotify_client = SpotifyClient(client_id)
    # Get playlists
    playlists = spotify_client.get_playlists()

    # Get tracks from playlists with (CLASS) in name
    tracks = []
    auto_playlist_id = None
    for playlist in playlists:
        if "(CLASS)" in playlist['name']:
            print(f"CLASS: {playlist['name']}")
            tracks.append(spotify_client.get_tracks(playlist['id']))
        elif "(AUTO)" in playlist['name']:
            auto_playlist_id = playlist['id']
            print(f"AUTO: {playlist['name']}")

    # Flatten list of tracks
    tracks = [j for sub in tracks for j in sub]
    # Check if they have an auto playlist
    if auto_playlist_id:
        spotify_client.add_tracks_to_playlist(tracks, auto_playlist_id)
    else:
        print("You do not have an (AUTO) playlist")

if __name__ == '__main__':
    run()
