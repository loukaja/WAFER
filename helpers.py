import requests
import shutil
import os.path
import os
import constants as c
from authentication import get_access_token

def build_headers():
    access_token = get_access_token()

    if access_token['expires_in'] > 0:
        authorization = 'Bearer ' + str(access_token['access_token'])

    headers = { 'accept': 'application/vnd.tidal.v1+json',
            'Authorization': authorization,
            'Content-Type': 'application/vnd.tidal.v1+json'}
    
    return headers

def get_release_information(url):

    headers = build_headers()

    r = requests.get(url=url, headers=headers)

    jsonResponse = r.json()

    day = jsonResponse['resource']['releaseDate'].split('-')[2]
    month = jsonResponse['resource']['releaseDate'].split('-')[1]
    year = jsonResponse['resource']['releaseDate'].split('-')[0]

    album_data = {}

    album_data['album_title'] = jsonResponse['resource']['title']
    album_data['artist'] = jsonResponse['resource']['artists'][0]['name']

    album_data['full_date'] = str(day) + ". " + c.KK[int(month)-1] + " " + str(year)
    album_data['total_min'], album_data['total_sec'] = divmod(jsonResponse['resource']['duration'], 60)

    return album_data

def get_tracklist(tracks_url):

    headers = build_headers()

    r = requests.get(url=tracks_url, headers=headers)
    jsonResponse = r.json()

    tracklist = []

    for i in jsonResponse['data']:
        track_num = i['resource']['trackNumber']
        title = i['resource']['title']
        duration = i['resource']['duration']
        minutes, seconds = divmod(duration, 60)

        track = {
            "track_number": track_num,
            "track_title": title,
            "track_minutes": minutes,
            "track_seconds": seconds
        }

        tracklist.append(track)

    return tracklist

def construct_path(artist, title):

    # Define the directory path
    directory = './albums/'

    # Ensure the directory exists, create it if it doesn't
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Construct the full file path
    path = os.path.join(directory, f"{artist.replace(' ', '_')}-{title.replace(' ', '_')}.txt")

    # Attempt to remove the file if it already exists
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    # Then start from scratch by copying the template file
    if not os.path.isfile(path):
        shutil.copyfile('./album_template.txt', path)

    return path

def get_all_artist_albums(artist_id):

    headers = build_headers()

    # Get all full length albums of artist /artists/{artistId}/albums

    artist_id = 24906
    #5436738

    url = f'https://openapi.tidal.com/artists/{artist_id}/albums?countryCode=US&limit=50'

    r = requests.get(url=url, headers=headers)

    jsonResponse = r.json()

    #pprint(jsonResponse)

    for i in jsonResponse['data']:
        if i['message'] != 'success':
            continue
        else:
            if i['resource']['type'] == 'ALBUM':
                print(i['resource']['title'])