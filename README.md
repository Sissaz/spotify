### Cloning the Repository

```bash
git clone https://github.com/Sissaz/spotify
```
### Create an App in Spotify for Developers
https://developer.spotify.com/dashboard/create

<div align="center"> 
  <a href="https://developer.spotify.com/dashboard/create">
    <img style="width:100%; max-width:1200px;" src="https://github.com/Sissaz/spotify/blob/master/src/assets/images/Create%20App.png?raw=true" />
  </a></div>


### Go to the App's settings and copy your Client_ID and Client_Secret
<br>
<div align="center"> 
  <a href="https://developer.spotify.com/dashboard/create">
    <img style="width:100%; max-width:1200px;" src="https://github.com/Sissaz/spotify/blob/master/src/assets/images/Client%20ID%20and%20Client%20Secret.png?raw=true" />
  </a></div>

### Create a new .env file in the cloned project folder with all the lines below, replacing only CLIENT_ID and CLIENT_SECRET
```bash
CLIENT_ID=YOUR_CLIENT_ID
CLIENT_SECRET=YOUR_CLIENT_SECRET
REDIRECT_URI=http://localhost:8888/callback
REFRESH_TOKEN=
```

### Run the following commands in PowerShell
```bash
cd src
```

```bash
cd assets
```

```bash
poetry install
```

```bash
poetry shell
```

```bash
poetry run python musicas_recentes.py
```


 #### [Python Code](https://github.com/Sissaz/spotify/blob/master/src/assets/musicas_recentes.py): ETL Pipeline Code

<div align="center"> 
  <a href="https://github.com/Sissaz/spotify/blob/master/src/assets/musicas_recentes.py">
    <img style="width:100%; max-width:1200px;" src="https://raw.githubusercontent.com/Sissaz/spotify/2dd829204aa15ef631ef529a8327f5eb2fcd2060/src/assets/images/diagrama.svg" />
  </a>
</div>