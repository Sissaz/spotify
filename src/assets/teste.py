import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv
from tokenspecial import gerar_token_usuario  # Corrigido o import

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

SPOTIFY_BASE_URL = "https://api.spotify.com/v1/me/player/recently-played"
VALOR_MAXIMO_SPOTIFY = 50

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
    musicas = []
    url = SPOTIFY_BASE_URL
    params = {
        'limit': VALOR_MAXIMO_SPOTIFY
    }

    while url:
        results = requisicao_spotify(url, headers, params)
        if results:
            for item in results['items']:
                musica = {
                    'nome': item['track']['name'],
                    'artista': item['track']['artists'][0]['name'],
                    'data_tocada': item['played_at']
                }
                musicas.append(musica)
            print(f"{len(musicas)} músicas recuperadas até agora.")
            
            # Verifica se há uma próxima página
            url = results['next']
            params = None  # Define os parâmetros como None nas próximas requisições
        else:
            break
        
        time.sleep(1)  # Pausa para evitar exceder limites da API

    return musicas

# Função para salvar as músicas em um arquivo CSV
def escrever_csv(musicas, output_filepath):
    df = pd.DataFrame(musicas)
    df.to_csv(output_filepath, index=False, encoding='utf-8')
    print(f"Escrita do arquivo CSV finalizada em {output_filepath}")

def main():
    output_filepath = 'musicas_ouvidas.csv'  # Caminho para o arquivo de saída CSV

    if not CLIENT_ID or not CLIENT_SECRET:
        print("Erro: CLIENT_ID ou CLIENT_SECRET não definidos.")
        return

    # Gera o token usando a função importada
    SPOTIFY_TOKEN = gerar_token_usuario(CLIENT_ID, CLIENT_SECRET)

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

if __name__ == '__main__':
    main()
