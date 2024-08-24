import os
import requests
import pandas as pd
import csv
from dotenv import load_dotenv
from gettoken import gerar_token_spotify  # Importa a função para gerar o token
import time

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

SPOTIFY_BASE_URL = "https://api.spotify.com/v1/"
VALOR_MAXIMO_SPOTIFY = 50

# Leitura do arquivo Excel
def ler_excel(filepath):
    data = pd.read_excel(filepath)
    return data['spotify_track_uri'].tolist()

# Função para fazer a requisição ao Spotify com tratamento de erros
def requisicao_spotify(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error occurred: {req_err}")
    return None

# Função para recuperar IDs dos artistas a partir dos IDs das faixas
def recuperar_ids_artistas(track_ids, headers):
    artists_id = []
    iterador = (len(track_ids) // VALOR_MAXIMO_SPOTIFY) + 1
    
    for index in range(iterador):
        start = index * VALOR_MAXIMO_SPOTIFY
        end = min((index + 1) * VALOR_MAXIMO_SPOTIFY, len(track_ids))

        ids = ','.join(track_ids[start:end])
        url = f"{SPOTIFY_BASE_URL}tracks?ids={ids}"

        results = requisicao_spotify(url, headers)
        if results:
            artists_id.extend([track['artists'][0]['id'] for track in results['tracks']])
            print(f"{index+1}/{iterador} requisições concluídas ({((index+1)*100)/iterador:.2f}% concluído)")
        
        time.sleep(1)  # Pausa para evitar exceder limites da API

    return artists_id

# Função para recuperar informações dos artistas a partir dos IDs dos artistas
def recuperar_artistas(artists_id, headers):
    artistas = []
    iterador = (len(artists_id) // VALOR_MAXIMO_SPOTIFY) + 1
    
    for index in range(iterador):
        start = index * VALOR_MAXIMO_SPOTIFY
        end = min((index + 1) * VALOR_MAXIMO_SPOTIFY, len(artists_id))

        ids = ','.join(artists_id[start:end])
        url = f"{SPOTIFY_BASE_URL}artists?ids={ids}"

        results = requisicao_spotify(url, headers)
        if results:
            for resposta_artista in results['artists']:
                artista = {
                    'id': resposta_artista['id'],
                    'nome': resposta_artista['name'],
                    'genres': resposta_artista['genres'],
                }
                artistas.append(artista)
            print(f"{index+1}/{iterador} requisições concluídas ({((index+1)*100)/iterador:.2f}% concluído)")
        
        time.sleep(1)  # Pausa para evitar exceder limites da API

    return artistas

# Função para escrever o CSV
def escrever_csv(artistas, output_filepath):
    with open(output_filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Id", "Nome", "Genero"])
        writer.writeheader()
        
        for artista in artistas:
            for genero in artista['genres']:
                writer.writerow({
                    'Id': artista['id'],
                    'Nome': artista['nome'],
                    'Genero': genero
                })
    print(f"Escrita do arquivo CSV finalizada em {output_filepath}")

def main():
    filepath = 'TracksId.xlsx'  # Caminho para o arquivo Excel com IDs de faixas
    output_filepath = 'generos.csv'  # Caminho para o arquivo de saída CSV

    if not CLIENT_ID or not CLIENT_SECRET:
        print("Erro: CLIENT_ID ou CLIENT_SECRET não definidos.")
        return

    # Gera o token usando a função importada
    SPOTIFY_TOKEN = gerar_token_spotify(CLIENT_ID, CLIENT_SECRET)

    headers = {
        'Authorization': f'Bearer {SPOTIFY_TOKEN}',
    }

    print("Iniciando...")

    # Ler IDs das faixas do Excel
    track_ids = ler_excel(filepath)

    if not track_ids:
        print("Erro: Nenhum ID de faixa encontrado no arquivo Excel.")
        return

    # Recuperar IDs dos artistas
    artists_id = recuperar_ids_artistas(track_ids, headers)

    if not artists_id:
        print("Erro: Nenhum ID de artista foi recuperado.")
        return

    # Recuperar informações dos artistas
    artistas = recuperar_artistas(artists_id, headers)

    if not artistas:
        print("Erro: Nenhuma informação de artista foi recuperada.")
        return

    # Escrever os dados no CSV
    escrever_csv(artistas, output_filepath)

if __name__ == '__main__':
    main()
