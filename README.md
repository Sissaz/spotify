## Spotify API Interaction and Data Collection Script
🎵 Download your recently played Spotify tracks data

This Python project automates the process of retrieving and storing recently played tracks from Spotify. It integrates with the Spotify API to fetch data, including track details, artist information, and playback timestamps. The data is then cleaned, processed, and saved into a CSV file, ensuring that no duplicate entries are stored. Additionally, the project includes a feature to insert the collected data into a PostgreSQL database, facilitating further analysis or integration with other systems. This solution is ideal for music enthusiasts and developers looking to maintain a personal log of their Spotify listening history or integrate it into larger applications.

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

### Create a new .env file in the cloned project 'src' folder with all the lines below, replacing only CLIENT_ID and CLIENT_SECRET
```bash
CLIENT_ID=YOUR_CLIENT_ID
CLIENT_SECRET=YOUR_CLIENT_SECRET
REDIRECT_URI=http://localhost:8888/callback
REFRESH_TOKEN=
```

### Run the following commands in PowerShell
```bash
pip install poetry
```

```bash
cd src
```

```bash
poetry env use 3.12.1
```

```bash
poetry install
```

```bash
cd assets
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
    <img style="width:100%; max-width:1200px;" src="https://raw.githubusercontent.com/Sissaz/spotify/390f1fe21b106977bcecb96694a92c0497b0a1d4/src/assets/images/diagrama.svg" />
  </a>
</div>