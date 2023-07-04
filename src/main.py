import pandas as pd
import os
from funciones import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

token = get_token()
# buscar artistas
artist_ids = search_for_artists(token, 'metal')

# coger albums de los artistas, comentar bloque cuando se cree el csv y cambiar claves
albums_list = []
for artist in artist_ids:
    albums_list.extend(get_albums(token, artist))

albums_df = pd.DataFrame(albums_list)
albums_df.to_csv('../data/albums.csv', index=False)

# coger canciones de los albums, comentar bloque cuando se cree el csv y cambiar claves
df = pd.read_csv('../data/albums.csv')
albums_list = df['album_id'].values

song_list = []
song_str_list = []
for album in albums_list:
    song_l, song_s = get_songs(token, album)#['album_id']
    song_list.extend(song_l)
    song_str_list.append(song_s)

songs_df = pd.DataFrame(song_list)
songs_df.to_csv('../data/songs.csv', index=False)

# coger caracteristicas de las canciones
df = pd.read_csv('../data/songs.csv')
songs_list = df['song_id'].values

 # solo acepta 100 por llamada
n = 0
song_str_list = []
songs_str = ''
for song in songs_list:
    if n == 99:
        songs_str += song
        song_str_list.append(songs_str)
        songs_str = ''
        n = 0
    else:
        songs_str += song + ','
        n += 1
songs_str = songs_str[:-1]
song_str_list.append(songs_str)

song_features = []
for songs in song_str_list:
    song_features.extend(get_songs_features(token, songs))

song_features_df = pd.DataFrame(song_features)
song_features_df.to_csv('../data/song_features.csv', index=False)
