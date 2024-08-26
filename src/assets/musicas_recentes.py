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
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')  # Armazena o refresh token
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
        refresh_token = token_info.get('refresh_token')  # Obtenha o refresh token
        
        print(f"Token de acesso: {access_token}")
        if refresh_token:
            print(f"Refresh Token: {refresh_token}")
        
        server_thread.shutdown()
        
        return access_token, refresh_token
    else:
        print(f"Erro ao gerar token: {response.status_code}")
        print(response.text)
        
        server_thread.shutdown()
        
        return None, None

def renovar_token_usuario(refresh_token, client_id, client_secret):
    token_url = "https://accounts.spotify.com/api/token"
    
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
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
        
        # Atualize o refresh token se necessário
        refresh_token = token_info.get('refresh_token', refresh_token)
        
        print(f"Novo token de acesso: {access_token}")
        return access_token, refresh_token
    else:
        print(f"Erro ao renovar token: {response.status_code}")
        print(response.text)
        return None, refresh_token

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

from datetime import datetime

from datetime import datetime, timedelta

# Função para recuperar as músicas recentemente ouvidas e associar ações de término
def recuperar_musicas(headers):
    url = SPOTIFY_BASE_URL
    params = {'limit': VALOR_MAXIMO_SPOTIFY}

    results = requisicao_spotify(url, headers, params)
    musicas = []

    if results:
        for item in results['items']:
            # Verifica se há imagens disponíveis e captura a primeira
            album_img_url = item['track']['album']['images'][0]['url'] if item['track']['album']['images'] else None

            # Extrai a data e a hora separadamente
            data_tocada = item['played_at']
            data, hora_completa = data_tocada.split('T')
            hora_completa = hora_completa.replace('Z', '')  # Remove o 'Z' do final da hora
            
            # Converte a hora para um objeto datetime para facilitar o arredondamento
            hora_obj = datetime.strptime(hora_completa, "%H:%M:%S.%f")
            # Arredonda para o segundo mais próximo
            if hora_obj.microsecond >= 500000:
                hora_obj += timedelta(seconds=1)
            hora_obj = hora_obj.replace(microsecond=0)

            # Formata a hora de volta para string
            hora = hora_obj.strftime("%H:%M:%S")

            musica = {
                'nome': item['track']['name'],
                'artista': item['track']['artists'][0]['name'],
                'data_tocada': data_tocada,
                'data': data,
                'hora': hora,
                'duration_ms': item['track']['duration_ms'],
                'spotify_track_uri': item['track']['uri'],
                'album_img': album_img_url
            }
            musicas.append(musica)
        print(f"{len(musicas)} músicas recuperadas.")

    return musicas


# Função para salvar as músicas em um arquivo CSV
def escrever_csv(musicas, output_filepath):
    df = pd.DataFrame(musicas)
    
    # Verifica se o arquivo já existe
    if os.path.isfile(output_filepath):
        # Se o arquivo existir, adiciona as novas linhas sem sobrescrever
        df.to_csv(output_filepath, mode='a', header=False, index=False, encoding='utf-8')
    else:
        # Se o arquivo não existir, cria um novo com cabeçalho
        df.to_csv(output_filepath, index=False, encoding='utf-8')
    
    print(f"Escrita do arquivo CSV finalizada em {output_filepath}")




# Função para salvar as músicas em um arquivo CSV
def escrever_csv(musicas, output_filepath):
    df = pd.DataFrame(musicas)
    
    # Verifica se o arquivo já existe
    if os.path.isfile(output_filepath):
        # Se o arquivo existir, adiciona as novas linhas sem sobrescrever
        df.to_csv(output_filepath, mode='a', header=False, index=False, encoding='utf-8')
    else:
        # Se o arquivo não existir, cria um novo com cabeçalho
        df.to_csv(output_filepath, index=False, encoding='utf-8')
    
    print(f"Escrita do arquivo CSV finalizada em {output_filepath}")

def main():
    global REFRESH_TOKEN  # Declara que usaremos a variável global REFRESH_TOKEN
    output_filepath = 'musicas_ouvidas.csv'  # Caminho para o arquivo de saída CSV

    if not CLIENT_ID or not CLIENT_SECRET:
        print("Erro: CLIENT_ID ou CLIENT_SECRET não definidos.")
        return

    # Tenta renovar o token de acesso usando o refresh token, se disponível
    if REFRESH_TOKEN:
        SPOTIFY_TOKEN, REFRESH_TOKEN = renovar_token_usuario(REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET)
    else:
        # Se não houver refresh token, autentique o usuário manualmente
        SPOTIFY_TOKEN, REFRESH_TOKEN = gerar_token_usuario(CLIENT_ID, CLIENT_SECRET)
    
    # Aguarda 5 segundos antes de prosseguir (você pode ajustar o tempo)
    time.sleep(5)

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

    # Atualiza o refresh token no .env
    with open('.env', 'r') as file:
        lines = file.readlines()
    with open('.env', 'w') as file:
        for line in lines:
            if line.startswith('REFRESH_TOKEN='):
                file.write(f'REFRESH_TOKEN={REFRESH_TOKEN}\n')
            else:
                file.write(line)

    # Finaliza o script
    sys.exit("Script finalizado com sucesso.")

if __name__ == '__main__':
    main()
