import pandas as pd
import requests
import time

# Seu arquivo CSV
csv_file_path = 'musicas_ouvidas.csv'
df = pd.read_csv(csv_file_path)

# Credenciais para a API do Spotify (você precisa substituir por suas próprias)
CLIENT_ID = 'xx'
CLIENT_SECRET = 'xx'

# Autenticação na API do Spotify
def get_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

token = get_token()
headers = {
    'Authorization': f'Bearer {token}',
}

# Função para buscar o ID do artista
def get_artist_id(artist_name):
    search_url = f'https://api.spotify.com/v1/search?q={artist_name}&type=artist'
    response = requests.get(search_url, headers=headers)
    data = response.json()
    artists = data.get('artists', {}).get('items', [])
    if artists:
        return artists[0]['id']
    return None

# Função para buscar os gêneros do artista
def get_artist_genres(artist_id):
    artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
    response = requests.get(artist_url, headers=headers)
    data = response.json()
    return data.get('genres', [])

# Iterar pelos artistas e buscar os gêneros
artist_genres = {}
for artist in df['artista'].unique():
    print(f"Buscando gêneros para o artista: {artist}")
    artist_id = get_artist_id(artist)
    if artist_id:
        genres = get_artist_genres(artist_id)
        artist_genres[artist] = genres
    else:
        artist_genres[artist] = []
    time.sleep(1)  # Para evitar ultrapassar o limite de requisições da API

# Adicionar os gêneros ao DataFrame e salvar
df['generos'] = df['artista'].map(artist_genres)
df.to_csv('musicas_ouvidas_com_generos.csv', index=False)
print("Arquivo atualizado com os gêneros foi salvo como 'musicas_ouvidas_com_generos.csv'.")
