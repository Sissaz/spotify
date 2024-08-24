import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

def gerar_token_spotify(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        expires_in = token_info['expires_in']
        print(f"Token gerado com sucesso! Token: {access_token}")
        print(f"O token expira em: {expires_in} segundos")
        return access_token
    else:
        print(f"Erro ao gerar token: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET

    if not client_id or not client_secret:
        print("Erro: CLIENT_ID ou CLIENT_SECRET não definidos.")
    else:
        token = gerar_token_spotify(client_id, client_secret)
