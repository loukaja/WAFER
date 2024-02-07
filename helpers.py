import requests
import shutil
import os.path
import os
import sys
from datetime import datetime

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

def get_release_information(url_id):

    headers = build_headers()

    # Construct the full URL based on the provided ID
    url = f'https://openapi.tidal.com/albums/{url_id}?countryCode=US'

    r = requests.get(url=url, headers=headers)
    
    if r.status_code == 451:
        sys.exit(f'{r.status_code}: Unavailable due to demand from the right-holders to prohibit access to the resource.')

    if r.status_code == 404:
        sys.exit(f'{r.status_code}: The requested resource {url} could not be found')

    if r.status_code == 200:
        jsonResponse = r.json()

        day = jsonResponse['resource']['releaseDate'].split('-')[2]
        month = jsonResponse['resource']['releaseDate'].split('-')[1]
        year = jsonResponse['resource']['releaseDate'].split('-')[0]

        album_data = {}

        album_data['album_title'] = jsonResponse['resource']['title']
        album_data['release_date'] = jsonResponse['resource']['releaseDate']
        album_data['artist'] = jsonResponse['resource']['artists'][0]['name']
        album_data['artist_id'] = jsonResponse['resource']['artists'][0]['id']

        album_data['full_date'] = str(day) + ". " + c.KK[int(month)-1] + " " + str(year)
        album_data['total_min'], album_data['total_sec'] = divmod(jsonResponse['resource']['duration'], 60)

        return album_data
    else:
        sys.exit(f'{r.status_code}: Something went wrong, please try again later')

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

    #artist_id = 24906
    #5436738

    url = f'https://openapi.tidal.com/artists/{artist_id}/albums?countryCode=US&limit=50'

    r = requests.get(url=url, headers=headers)

    jsonResponse = r.json()

    all_albums = []

    for i in jsonResponse['data']:
        if i['status'] == 451:
            album = {
                "title": "Not available",
                "release_date": "Not available"
            }
            all_albums.append(album)
        else:
            if i['resource']['type'] == 'ALBUM':
                album = {
                    "title": i['resource']['title'],
                    "release_date": i['resource']['releaseDate']
                }
                
                all_albums.append(album)
    
    # Sort the albums in release order before returning them
    #all_albums.sort(key=lambda x: x['release_date'], reverse=True)
    
    return all_albums

def get_previous_album(current_album):
    all_albums = get_all_artist_albums(current_album['artist_id'])

    current_album_index = None

    # Find the index of the current album in the list
    for i, album in enumerate(all_albums):
        if album['title'] == current_album['album_title']:
            current_album_index = i
            break

    # If current_album not found, return None
    if current_album_index is None:
        return None

    # Iterate over albums starting from the one after current_album
    for album in all_albums[current_album_index + 1:]:
        release_date_str = album['release_date']

        # Check if the release date is 'Not available' - if it is, we assume it's a different
        # album than current_album because the information was not available
        if release_date_str == 'Not available':
            return None

        # If a valid release date is found, check that it's not the same album
        if release_date_str:
            if album['title'] == current_album['album_title']:
                continue
            else:
                previous_album = {
                    "title": album['title'],
                    "year": release_date_str.split('-')[0]  # Use release date string directly if datetime parsing fails
                }
                return previous_album

    # Return None if no previous album is found
    return None