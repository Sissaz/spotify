De um git clone

<br>
Faça um App no Spotify for Developers:
https://developer.spotify.com/dashboard/create

<div align="center"> 
  <a href="https://developer.spotify.com/dashboard/create">
    <img style="width:100%; max-width:1200px;" src="https://github.com/Sissaz/spotify/blob/master/src/assets/images/Create%20App.png?raw=true" />
  </a></div>

<br>
Entre na configuração do App e copie o Client_ID e Client_Secret

<div align="center"> 
  <a href="https://developer.spotify.com/dashboard/create">
    <img style="width:100%; max-width:1200px;" src="https://github.com/Sissaz/spotify/blob/master/src/assets/images/Client%20ID%20and%20Client%20Secret.png?raw=true" />
  </a></div>

Crie um novo arquivo .env na pasta do projeto clonado, com todas as linhas abaixo e substitua apenas CLIENT_ID e CLIENT_SECRET
CLIENT_ID=SEU_CLIENT_ID
CLIENT_SECRET=SEU_CLIENT_SECRET
REDIRECT_URI=http://localhost:8888/callback
REFRESH_TOKEN=

<br>
Execute os seguintes comandos no PowerShell:
cd src
cd assets
poetry install
poetry shell
poetry run python musicas_recentes.py

<br>
 #### [Python Code](https://github.com/Sissaz/spotify/blob/master/src/assets/musicas_recentes.py): ETL Pipeline Code
<br>
<div align="center"> 
  <a href="https://github.com/Sissaz/spotify/blob/master/src/assets/musicas_recentes.py">
    <img style="width:100%; max-width:1200px;" src="https://raw.githubusercontent.com/Sissaz/spotify/2dd829204aa15ef631ef529a8327f5eb2fcd2060/src/assets/images/diagrama.svg" />
  </a>
</div>