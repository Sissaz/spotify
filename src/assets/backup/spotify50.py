import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Configura a autenticação com a API do Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="user-read-recently-played user-library-read"))

def get_all_played_tracks():
    tracks = []
    results = sp.current_user_recently_played(limit=50)
    tracks.extend(results['items'])
    
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    
    return tracks

def extract_artists_from_tracks(tracks):
    records = []
    
    for item in tracks:
        track = item['track']
        played_at = item['played_at']
        track_name = track['name']
        
        for artist in track['artists']:
            artist_id = artist['id']
            artist_name = artist['name']
            genres = sp.artist(artist_id)['genres']
            
            records.append({
                "artist_name": artist_name,
                "genres": ', '.join(genres),
                "track_name": track_name,
                "played_at": played_at
            })
    
    return records

# Busca as últimas músicas ouvidas
played_tracks = get_all_played_tracks()

# Extrai as informações das músicas e artistas
records = extract_artists_from_tracks(played_tracks)

# Nome do arquivo CSV
csv_filename = 'played_tracks.csv'

# Escreve os dados no arquivo CSV
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["artist_name", "genres", "track_name", "played_at"])
    writer.writeheader()
    writer.writerows(records)

print(f"Informações das últimas músicas reproduzidas salvas em {csv_filename}")