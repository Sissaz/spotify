import os
import requests
import webbrowser  # Adicionando a importação do módulo webbrowser
from flask import Flask, request
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "user-read-recently-played"

app = Flask(__name__)
auth_code = None

# Função para gerar o token com permissões de usuário
def gerar_token_usuario(client_id, client_secret):
    global auth_code
    # Primeiro passo: redirecionar o usuário para a página de autorização
    auth_url = ("https://accounts.spotify.com/authorize"
                "?response_type=code"
                f"&client_id={client_id}"
                f"&scope={SCOPES.replace(' ', '%20')}"
                f"&redirect_uri={REDIRECT_URI}")
    
    # Abre a URL de autorização no navegador
    webbrowser.open(auth_url)

    # Inicia um servidor Flask para capturar o código de autorização
    app.run(port=8888, debug=False)

    # Segundo passo: trocar o código pelo token de acesso
    token_url = "https://accounts.spotify.com/api/token"
    
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=payload, headers=headers)
    
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        return access_token
    else:
        print(f"Erro ao gerar token: {response.status_code}")
        print(response.text)
        return None

@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    return "Autorização recebida! Você pode fechar esta janela."

if __name__ == "__main__":
    token = gerar_token_usuario(CLIENT_ID, CLIENT_SECRET)
    if token:
        print(f"Token de acesso: {token}")
    else:
        print("Não foi possível obter o token de acesso.")