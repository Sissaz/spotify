import os
import requests
import webbrowser
import threading
import time
import pandas as pd
import sys
from flask import Flask, request, redirect
from dotenv import load_dotenv
from werkzeug.serving import make_server

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "user-read-recently-played"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1/me/player/recently-played"
VALOR_MAXIMO_SPOTIFY = 50

app = Flask(__name__)
auth_code = None

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('localhost', 8888, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    return redirect("/success")

@app.route('/success')
def success():
    # Fecha automaticamente a aba do navegador após a autenticação
    return """
    <h1>Autorização recebida! Você pode fechar esta janela.</h1>
    <script>
    window.close();
    </script>
    """

def gerar_token_usuario(client_id, client_secret):
    global auth_code

    auth_url = ("https://accounts.spotify.com/authorize"
                "?response_type=code"
                f"&client_id={client_id}"
                f"&scope={SCOPES.replace(' ', '%20')}"
                f"&redirect_uri={REDIRECT_URI}")
    
    webbrowser.open(auth_url)

    server_thread = ServerThread(app)
    server_thread.start()

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
        
        # Encerra o servidor Flask
        server_thread.shutdown()
        
        return access_token
    else:
        print(f"Erro ao gerar token: {response.status_code}")
        print(response.text)
        
        # Encerra o servidor Flask em caso de erro
        server_thread.shutdown()
        
        return None

# Função para fazer a requisição ao Spotify com tratamento de erros
def requisicao_spotify(url, headers, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error occurred: {req_err}")
    return None

# Função para recuperar as músicas recentemente ouvidas
def recuperar_musicas(headers):
    url = SPOTIFY_BASE_URL
    params = {'limit': VALOR_MAXIMO_SPOTIFY}

    results = requisicao_spotify(url, headers, params)
    musicas = []

    if results:
        for item in results['items']:
            musica = {
                'nome': item['track']['name'],
                'artista': item['track']['artists'][0]['name'],
                'data_tocada': item['played_at']
            }
            musicas.append(musica)
        print(f"{len(musicas)} músicas recuperadas.")

    return musicas

# Função para salvar as músicas em um arquivo CSV
def escrever_csv(musicas, output_filepath):
    df = pd.DataFrame(musicas)
    df.to_csv(output_filepath, index=False, encoding='utf-8')
    print(f"Escrita do arquivo CSV finalizada em {output_filepath}")

def main():
    output_filepath = 'musicas_recentes.csv'  # Caminho para o arquivo de saída CSV

    if not CLIENT_ID or not CLIENT_SECRET:
        print("Erro: CLIENT_ID ou CLIENT_SECRET não definidos.")
        return

    # Gera o token usando a função importada
    SPOTIFY_TOKEN = gerar_token_usuario(CLIENT_ID, CLIENT_SECRET)

    # Aguarda 5 segundos antes de prosseguir (você pode ajustar o tempo)
    time.sleep(3)

    headers = {
        'Authorization': f'Bearer {SPOTIFY_TOKEN}',
    }

    print("Iniciando...")

    # Recuperar músicas ouvidas
    musicas = recuperar_musicas(headers)

    if not musicas:
        print("Erro: Nenhuma música foi recuperada.")
        return

    # Escrever os dados no CSV
    escrever_csv(musicas, output_filepath)

    # Finaliza o script
    sys.exit("Script finalizado com sucesso.")

if __name__ == '__main__':
    main()
