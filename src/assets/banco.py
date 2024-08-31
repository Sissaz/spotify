import pandas as pd
import psycopg2
from psycopg2 import sql
import requests
from tqdm import tqdm  # Biblioteca para barra de progresso

# URL do arquivo CSV no GitHub
url = 'https://raw.githubusercontent.com/Sissaz/spotify/master/src/assets/musicas_ouvidas.csv'

print("Baixando o arquivo CSV do GitHub...")
df = pd.read_csv(url)
print("Arquivo CSV baixado e carregado com sucesso!")

# Conectar ao banco de dados PostgreSQL
print("Conectando ao banco de dados PostgreSQL...")
connection = psycopg2.connect(
    host="dpg-cr9ormbv2p9s73bbr3sg-a.oregon-postgres.render.com",
    database="spotify_txnb",
    user="spotify_txnb_user",
    password="7wYhqm9CroBfi9DasUpnYtcFAKadlfOL"
)
cursor = connection.cursor()
print("Conexão ao banco de dados estabelecida com sucesso!")

# Criar a tabela no banco de dados (se ainda não existir) com chave única
print("Verificando se a tabela 'musicas_ouvidas' existe e criando se necessário...")
create_table_query = '''
CREATE TABLE IF NOT EXISTS musicas_ouvidas (
    nome TEXT,
    artista TEXT,
    data_completa TIMESTAMP,
    data DATE,
    duracao_ms INTEGER,
    duracao_min TIME,  -- Tipo TIME para duracao_min
    hora_inicio TIME,
    hora_fim TIME,
    spotify_track_uri TEXT,
    album_img TEXT,
    UNIQUE(nome, artista, data_completa)  -- Chave única
);
'''
cursor.execute(create_table_query)
connection.commit()
print("Tabela verificada/criada com sucesso!")

# Inserir os dados do CSV na tabela com barra de progresso
print("Inserindo os dados do CSV na tabela...")
for index, row in tqdm(df.iterrows(), total=len(df)):
    try:
        insert_query = sql.SQL("""
            INSERT INTO musicas_ouvidas (nome, artista, data_completa, data, duracao_ms, duracao_min, hora_inicio, hora_fim, spotify_track_uri, album_img)
            VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {})
        """).format(
            sql.Literal(row['nome']),
            sql.Literal(row['artista']),
            sql.Literal(row['data_completa']),
            sql.Literal(row['data']),
            sql.Literal(row['duracao_ms']),
            sql.Literal(row['duracao_min']),  # Inserir duracao_min como TIME
            sql.Literal(row['hora_inicio']),
            sql.Literal(row['hora_fim']),
            sql.Literal(row['spotify_track_uri']),
            sql.Literal(row['album_img'])
        )
        cursor.execute(insert_query)
    except psycopg2.IntegrityError:
        connection.rollback()  # Ignora a inserção e continua com os outros registros

connection.commit()
print("Dados inseridos com sucesso!")

# Fechar a conexão com o banco de dados
cursor.close()
connection.close()
print("Conexão com o banco de dados fechada.")
