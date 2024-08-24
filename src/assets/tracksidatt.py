import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time
from tokenspecial import gerar_token_usuario  # Importa a função para gerar o token

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

SPOTIFY_BASE_URL = "https://api.spotify.com/v1/"
VALOR_MAXIMO_SPOTIFY = 50

# Gera o token usando a função importada
SPOTIFY_TOKEN = gerar_token_usuario(CLIENT_ID, CLIENT_SECRET)

# Headers de autenticação
headers = {
    'Authorization': f'Bearer {SPOTIFY_TOKEN}',
}

def requisicao_spotify(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error occurred: {e}")
    return None

# Função para obter todo o histórico de faixas reproduzidas
def obter_historico_completo(headers):
    track_ids = []
    url = f"{SPOTIFY_BASE_URL}me/player/recently-played?limit={VALOR_MAXIMO_SPOTIFY}"

    while url:
        results = requisicao_spotify(url, headers)
        if results is not None and 'items' in results:
            for item in results['items']:
                track_id = item['track']['uri'].split(':')[2]  # Extrai o ID da URI
                track_ids.append(track_id)
            
            # Verifica se 'cursors' está presente e contém o 'before'
            if results.get('cursors') and 'before' in results['cursors']:
                before_cursor = results['cursors']['before']
                url = f"{SPOTIFY_BASE_URL}me/player/recently-played?limit={VALOR_MAXIMO_SPOTIFY}&before={before_cursor}"
                print(f"Obtidas {len(track_ids)} faixas até agora...")
            else:
                print("Nenhum cursor 'before' encontrado ou valor nulo. Finalizando a coleta.")
                break
            
            time.sleep(1)  # Pausa para evitar exceder limites da API
        else:
            print("Nenhum resultado adicional encontrado ou erro na requisição.")
            break

    # Remover duplicatas
    track_ids = list(set(track_ids))
    return track_ids

# Função para salvar IDs em um arquivo Excel
def salvar_ids_excel(track_ids, filepath):
    df = pd.DataFrame(track_ids, columns=["spotify_track_uri"])
    df.to_excel(filepath, index=False)
    print(f"Arquivo Excel salvo em: {filepath}")

def main():
    output_filepath = 'TracksId.xlsx'  # Caminho para salvar o arquivo Excel

    print("Iniciando...")

    # Obter o histórico completo de faixas reproduzidas
    track_ids = obter_historico_completo(headers)
    
    if not track_ids:
        print("Nenhuma faixa encontrada no histórico.")
        return

    # Salvar os IDs em um arquivo Excel
    salvar_ids_excel(track_ids, output_filepath)

if __name__ == '__main__':
    main()
