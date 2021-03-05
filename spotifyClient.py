import threading
import base64
import webbrowser
import requests

class SpotifyClient:

    def __init__(self, client_id):
        redirect_uri = "http://localhost.com:8888/callback/"
        url = f"https://accounts.spotify.com/authorize?client_id={client_id}" \
              f"&response_type=code&redirect_uri={redirect_uri}&" \
              "scope=user-read-private%20playlist-modify-public%20playlist-modify-private%20playlist-read-private&" \
              "state=34fFs29kd09"
        webbrowser.open(url)
        inputURL = input("Copy and paste URL: ")
        code = inputURL[inputURL.index("code=") + 5: inputURL.index("&state=")]

        client_secret = input("Client Secret: ")
        authorization_string = f"{client_id}:{client_secret}"
        authorization_bytes = authorization_string.encode('ascii')
        self.authorization = base64.b64encode(authorization_bytes).decode('ascii')

        url = f"https://accounts.spotify.com/api/token"
        response = requests.post(
            url,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                "Authorization": f"Basic {self.authorization}"
            },
            data={
                "grant_type": 'authorization_code',
                "code": code,
                "redirect_uri": redirect_uri
            }
        )
        response_json = response.json()

        self.access_token = response_json['access_token']
        self.refresh_token = response_json['refresh_token']
        threading.Timer(3540, self.refresh_access).start()

    def refresh_access(self):
        headers = {
            'Authorization': f"Basic {self.authorization}"
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        response_json = response.json()

        self.access_token = response_json['access_token']
        threading.Timer(3540, self.refresh_access).start()

    def get_playlists(self):
        url = "https://api.spotify.com/v1/me/playlists"

        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        )

        response_json = response.json()

        playlists = [playlist for playlist in response_json['items']]

        print(f"Found {len(playlists)} playlists in your library")
        return playlists

    def get_tracks(self, playlist_id):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        )

        playlist = response.json()["tracks"]

        tracks = [track for track in playlist['items']]
        while playlist["next"]:
            url = playlist['next']
            response = requests.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            playlist = response.json()
            next_tracks = [track for track in playlist['items']]
            tracks.extend(next_tracks)

        return tracks

    def add_tracks_to_playlist(self, tracks, playlist_id):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        existing_tracks = self.get_tracks(playlist_id)

        existing_tracks_ids = [track['track']['id'] for track in existing_tracks]
        track_ids_json = []
        for track in tracks:
            if track['track']['id'] not in existing_tracks_ids:
                track_ids_json.append(f"spotify:track:{track['track']['id']}")
                print(f"Added track: {track['track']['name']}")

        if not track_ids_json == []:
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.access_token}"
                },
                json={
                    'uris': track_ids_json
                }
            )

            return response.ok
        print("No songs to add")
        return
