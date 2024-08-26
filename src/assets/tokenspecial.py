import os
import requests
import webbrowser
import threading
import time
from flask import Flask, request, redirect
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "user-read-recently-played"

app = Flask(__name__)
auth_code = None
shutdown_requested = False

@app.route('/callback')
def callback():
    global auth_code
    global shutdown_requested
    auth_code = request.args.get('code')
    shutdown_requested = True  # Sinaliza que o servidor pode ser encerrado
    return redirect("/success")

@app.route('/success')
def success():
    return "<h1>Autorização recebida! Você pode fechar esta janela.</h1>"

def run_flask_app():
    app.run(port=8888)

def gerar_token_usuario(client_id, client_secret):
    global auth_code
    global shutdown_requested

    auth_url = ("https://accounts.spotify.com/authorize"
                "?response_type=code"
                f"&client_id={client_id}"
                f"&scope={SCOPES.replace(' ', '%20')}"
                f"&redirect_uri={REDIRECT_URI}")
    
    webbrowser.open(auth_url)

    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    while auth_code is None:
        time.sleep(0.1)

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
        
        print(f"Token de acesso: {access_token}")
        
        # Aguarda até que o servidor Flask possa ser encerrado
        while not shutdown_requested:
            time.sleep(0.1)
        
        return access_token
    else:
        print(f"Erro ao gerar token: {response.status_code}")
        print(response.text)
        
        return None

if __name__ == "__main__":
    token = gerar_token_usuario(CLIENT_ID, CLIENT_SECRET)
    if not token:
        print("Não foi possível obter o token de acesso.")
    # O servidor Flask deve encerrar após a conclusão
    os._exit(0)  # Encerramento forçado para garantir que o Flask pare