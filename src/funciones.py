import base64
from requests import post, get
import json
from variables import *

def get_token():
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'content-type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    return json_result['access_token']

def get_auth_header(token):
    return {'Authorization': 'Bearer ' + token,}

def search_for_artists(token, genre):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f'?q=genre:{genre}&type=artist&market=ES&limit=50'
    query_url = url + query
    artist_ids = []

    while True:
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)
        if not json_result['artists']['next']:
            for i in json_result['artists']['items']:
                artist_ids.append(i['id'])
            break
        query_url = json_result['artists']['next']
        for i in json_result['artists']['items']:
            artist_ids.append(i['id'])
    return artist_ids

def get_albums(token, artist_id):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    headers = get_auth_header(token)
    query = f'?include_groups=album&market=ES&limit=20'
    query_url = url + query
    album_list = []

    while True:
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)
        if json_result['total'] < 4: # solo si el grupo tiene mas de 3 albumes
            break
        if not json_result['next']:
            for i in json_result['items']:
                repetido = False
                for j in album_list:
                    if j['release_date'] == i['release_date']:
                        repetido = True
                        break
                if not repetido:
                    album_list.append({
                        'album_id': i['id'],
                        'album_name': i['name'],
                        'release_date': i['release_date'],
                        'release_date_precision': i['release_date_precision']
                    })
            break
        query_url = json_result['next']
        for i in json_result['items']:
            repetido = False
            for j in album_list:
                if j['release_date'] == i['release_date']:
                    repetido = True
                    break
            if not repetido:
                album_list.append({
                    'album_id': i['id'],
                    'album_name': i['name'],
                    'release_date': i['release_date'],
                    'release_date_precision': i['release_date_precision']
                })
    return album_list

def get_songs(token, album_id):
    url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
    headers = get_auth_header(token)
    query = f'?market=ES&limit=50'
    query_url = url + query
    song_list = []
    songs_str = []

    while True:
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)
        if not json_result['next']:
            for i in json_result['items']:
                song_list.append({
                    'album_id': album_id,
                    'song_id': i['id'],
                    'song_name': i['name'],
                    'artist': i['artists'][0]['name']
                })
                songs_str.append(i['id'])
            break
        query_url = json_result['next']
        for i in json_result['items']:
            song_list.append({
                'album_id': album_id,
                'song_id': i['id'],
                'song_name': i['name'],
                'artist': i['artists'][0]['name']
            })
            songs_str.append(i['id'])
    return song_list, ','.join(songs_str)

def get_songs_features(token, songs_str):
    query_url = f'https://api.spotify.com/v1/audio-features/?ids={songs_str}'
    headers = get_auth_header(token)
    song_features_list = []

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)

    for song in json_result['audio_features']:
        if song:
            song_features_list.append({
                'song_id': song['id'],
                'acousticness': song['acousticness'], # no electrico 0-1
                'energy': song['energy'], # 0-1
                'loudness': song['loudness'], #-60dB-0
                'valence': song['valence'], # 0(sad, angry)-1(happy,cheerful)
                'tempo(BPM)': song['tempo'] # velocidad
            })

    return song_features_list
