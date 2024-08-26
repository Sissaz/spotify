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
from datetime import datetime, timedelta

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Carrega os valores do CLIENT_ID, CLIENT_SECRET, e REFRESH_TOKEN a partir das variáveis de ambiente
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')  # Armazena o refresh token
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "user-read-recently-played"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1/me/player/recently-played"
VALOR_MAXIMO_SPOTIFY = 50  # Limite máximo de músicas a serem recuperadas por requisição

# Inicializa o aplicativo Flask
app = Flask(__name__)
auth_code = None  # Variável global para armazenar o código de autorização

# Classe que executa o servidor Flask em uma thread separada
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

# Rota que captura o código de autorização após o usuário permitir o acesso
@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')  # Captura o código de autorização da URL
    return redirect("/success")  # Redireciona para a página de sucesso

# Rota de sucesso que exibe uma mensagem para fechar a janela
@app.route('/success')
def success():
    return """
    <h1>Autorização recebida! Você pode fechar esta janela.</h1>
    <script>
    window.close();
    </script>
    """

# Função para gerar o token de acesso do usuário
def gerar_token_usuario(client_id, client_secret):
    global auth_code

    # URL de autorização para obter o código de autorização
    auth_url = ("https://accounts.spotify.com/authorize"
                "?response_type=code"
                f"&client_id={client_id}"
                f"&scope={SCOPES.replace(' ', '%20')}"
                f"&redirect_uri={REDIRECT_URI}")
    
    # Abre a URL de autorização no navegador
    webbrowser.open(auth_url)

    # Inicia o servidor Flask em uma thread separada
    server_thread = ServerThread(app)
    server_thread.start()

    # Aguarda até que o código de autorização seja recebido
    while auth_code is None:
        time.sleep(0.1)

    # URL para obter o token de acesso
    token_url = "https://accounts.spotify.com/api/token"
    
    # Dados para a requisição do token
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

    # Faz a requisição para obter o token de acesso
    response = requests.post(token_url, data=payload, headers=headers)
    
    if response.status_code == 200:
        # Se a resposta for bem-sucedida, captura o token de acesso e o refresh token
        token_info = response.json()
        access_token = token_info['access_token']
        refresh_token = token_info.get('refresh_token')  # Obtenha o refresh token
        
        print(f"Token de acesso: {access_token}")
        if refresh_token:
            print(f"Refresh Token: {refresh_token}")
        
        server_thread.shutdown()  # Encerra o servidor Flask
        
        return access_token, refresh_token
    else:
        # Em caso de erro, imprime a mensagem de erro
        print(f"Erro ao gerar token: {response.status_code}")
        print(response.text)
        
        server_thread.shutdown()  # Encerra o servidor Flask
        
        return None, None

# Função para renovar o token de acesso usando o refresh token
def renovar_token_usuario(refresh_token, client_id, client_secret):
    token_url = "https://accounts.spotify.com/api/token"
    
    # Dados para a requisição de renovação do token
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Faz a requisição para renovar o token de acesso
    response = requests.post(token_url, data=payload, headers=headers)
    
    if response.status_code == 200:
        # Se a resposta for bem-sucedida, captura o novo token de acesso
        token_info = response.json()
        access_token = token_info['access_token']
        
        # Atualiza o refresh token se necessário
        refresh_token = token_info.get('refresh_token', refresh_token)
        
        print(f"Novo token de acesso: {access_token}")
        return access_token, refresh_token
    else:
        # Em caso de erro, imprime a mensagem de erro
        print(f"Erro ao renovar token: {response.status_code}")
        print(response.text)
        return None, refresh_token

# Função para fazer a requisição ao Spotify com tratamento de erros
def requisicao_spotify(url, headers, params=None):
    try:
        # Faz a requisição GET ao Spotify
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Levanta uma exceção para códigos de status de erro
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error occurred: {req_err}")
    return None

# Função para recuperar as músicas ouvidas recentemente no Spotify
def recuperar_musicas(headers):
    url = SPOTIFY_BASE_URL
    params = {'limit': VALOR_MAXIMO_SPOTIFY}  # Limite máximo de músicas a serem recuperadas

    results = requisicao_spotify(url, headers, params)
    musicas = []

    if results:
        for item in results['items']:
            # Verifica se há imagens disponíveis e captura a primeira
            album_img_url = item['track']['album']['images'][0]['url'] if item['track']['album']['images'] else None

            # Extrai a data e a hora da música tocada
            data_tocada = item['played_at']

            # Converte a string de data e hora para um objeto datetime
            dt_utc = datetime.strptime(data_tocada, "%Y-%m-%dT%H:%M:%S.%fZ")
            
            # Subtrai 3 horas para ajustar para GMT-3
            dt_gmt3 = dt_utc - timedelta(hours=3)
            
            # Separa a data e a hora
            data = dt_gmt3.strftime("%Y-%m-%d")
            hora = dt_gmt3.strftime("%H:%M:%S")

            # Converte a duração de milissegundos para minutos e segundos
            duration_ms = item['track']['duration_ms']
            minutes = duration_ms // 60000  # divide por 60.000 para obter os minutos
            seconds = (duration_ms % 60000) // 1000  # o restante é convertido em segundos
            duration_min_sec = f"{minutes:02}:{seconds:02}"  # formata em MM:SS

            # Calcula a hora de término somando a hora inicial com a duração
            end_time = dt_gmt3 - timedelta(minutes=minutes, seconds=seconds)
            hora_inicio = end_time.strftime("%H:%M:%S")

            # Cria um dicionário com os dados da música
            musica = {
                'nome': item['track']['name'],
                'artista': item['track']['artists'][0]['name'],
                'data_completa': data_tocada,
                'data': data,
                'duracao_ms': duration_ms,
                'duracao_min': duration_min_sec,
                'hora_inicio': hora_inicio,
                'hora_fim': hora,
                'spotify_track_uri': item['track']['uri'],
                'album_img': album_img_url
            }
            musicas.append(musica)  # Adiciona a música à lista
        print(f"{len(musicas)} músicas recuperadas.")

    return musicas

# Função para escrever os dados das músicas em um arquivo CSV
def escrever_csv(musicas, output_filepath):
    df = pd.DataFrame(musicas)  # Converte a lista de músicas em um DataFrame
    
    # Verifica se o arquivo já existe
    if os.path.isfile(output_filepath):
        # Carrega o CSV existente
        df_existente = pd.read_csv(output_filepath)
        
        # Concatena as novas linhas com as existentes, adicionando as novas linhas no topo
        df_final = pd.concat([df, df_existente], ignore_index=True)
    else:
        # Se o arquivo não existir, apenas use as novas linhas
        df_final = df
    
    # Remove duplicatas com base em todas as colunas
    df_final.drop_duplicates(inplace=True)
    
    # Salva o DataFrame final no arquivo CSV, mantendo o cabeçalho
    df_final.to_csv(output_filepath, index=False, encoding='utf-8')
    
    print(f"Arquivo CSV atualizado com novas linhas no topo e duplicatas removidas. Salvo em {output_filepath}")

# Função principal que orquestra a execução do script
def main():
    global REFRESH_TOKEN  # Declara que usaremos a variável global REFRESH_TOKEN
    output_filepath = 'musicas_ouvidas.csv'  # Caminho para o arquivo de saída CSV

    # Verifica se CLIENT_ID ou CLIENT_SECRET estão definidos
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

    # Configura os cabeçalhos de autorização para a requisição ao Spotify
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

    # Atualiza o refresh token no arquivo .env
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

# Ponto de entrada do script
if __name__ == '__main__':
    main()
