"""Module that hosts various helper function
"""

import os
import os.path
import sys
import shutil
import requests

import constants as c
from authentication import Authentication
from review_scraper import get_review

access_token = Authentication()

def build_headers():
    """Helper function to build headers

    Returns:
        dict: header
    """

    if access_token.expires_in == 0:
        access_token.refresh_access_token()

    authorization = 'Bearer ' + access_token.access_token

    headers = { 'accept': 'application/vnd.tidal.v1+json',
            'Authorization': authorization,
            'Content-Type': 'application/vnd.tidal.v1+json'}

    return headers

def get_release_information(url_id):
    """Function that fetches album information

    Args:
        url_id (string): The last numerical part of tidals album browse URL

    Returns:
        dict: A dictionary with album title, release date, artist, artist ID and running time
    """

    headers = build_headers()

    # Construct the full URL based on the provided ID
    url = f'https://openapi.tidal.com/albums/{url_id}?countryCode=US'

    try:
        response = requests.get(url=url, headers=headers, timeout=(3,5))

        if response.status_code == 451:
            sys.exit(f'{response.status_code}: Unavailable due to demand from the right-holders to \
                      prohibit access to the resource.')

        if response.status_code == 404:
            sys.exit(f'{response.status_code}: The requested resource {url} could not be found')

        if response.status_code == 200:
            json_response = response.json()

            day = json_response['resource']['releaseDate'].split('-')[2]
            month = json_response['resource']['releaseDate'].split('-')[1]
            year = json_response['resource']['releaseDate'].split('-')[0]

            album_data = {}

            album_data['album_title'] = json_response['resource']['title']
            album_data['artist'] = json_response['resource']['artists'][0]['name']
            album_data['artist_id'] = json_response['resource']['artists'][0]['id']

            album_data['full_date'] = str(day) + ". " + c.KK[int(month)-1] + " " + str(year)
            album_data['total_min'], album_data['total_sec'] = \
                  divmod(json_response['resource']['duration'], 60)

            return album_data

        sys.exit(f'{response.status_code}: Something went wrong, please try again later')
    except requests.exceptions.Timeout:
        sys.exit("The request timed out")
    except requests.exceptions.RequestException as e:
        sys.exit("An error occurred:", e)

def get_tracklist(tracks_url):
    """Function that generates album tracklist

    Args:
        tracks_url (string): Tidal album ID

    Returns:
        list: A list of dictionaries of tracks holding track number, title, minutes and seconds
    """

    headers = build_headers()

    try:
        response = requests.get(url=tracks_url, headers=headers, timeout=(3, 5))
        json_response = response.json()

        tracklist = []

        for i in json_response['data']:
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
    except requests.exceptions.Timeout:
        sys.exit("The request timed out")
    except requests.exceptions.RequestException as e:
        sys.exit("An error occurred:", e)

def construct_path(artist, title):
    """Function that creates the output file

    Args:
        artist (string): Name of the artist
        title (string): Name of the album

    Returns:
        string: A path to the file the function created
    """

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
            print(f'Error: {e.filename} - {e.strerror}.')

    # Then start from scratch by copying the template file
    if not os.path.isfile(path):
        shutil.copyfile('./album_template.txt', path)

    return path

def get_all_artist_albums(artist_id):
    """Function to get all albums by artist

    Args:
        artist_id (string): Tidal ID of the artist

    Returns:
        list: A list of dictionaries of artists' albums, with title and release date
    """

    headers = build_headers()

    url = f'https://openapi.tidal.com/artists/{artist_id}/albums?countryCode=US&limit=50'

    try:
        response = requests.get(url=url, headers=headers, timeout=(3,5))

        json_response = response.json()

        all_albums = []

        for i in json_response['data']:
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

        return all_albums
    except requests.exceptions.Timeout:
        sys.exit("The request timed out")
    except requests.exceptions.RequestException as e:
        sys.exit("An error occurred:", e)

def get_previous_album(current_album):
    """Function to get previous album information

    Args:
        current_album (dict): The album initially searched for

    Returns:
        dict: If available, returns a dict with the title and release date of the previous album.
       If not, returns None 
    """

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

            previous_album = {
                "title": album['title'],
                # Use release date string directly if datetime parsing fails
                "year": release_date_str.split('-')[0]
            }
            return previous_album

    # Return None if no previous album is found
    return None

def fill_album_info_box(url_id):
    """Function that writes the information to the created file

    Args:
        url_id (string): The last part of the Tidal browse album URL

    Returns:
        list: A list with the file path and the album data
    """

    # Get artist and album name, duration, release date and previous album title and release date
    album_data = get_release_information(url_id)
    previous_album = get_previous_album(album_data)

    # Create new file from template
    file = construct_path(album_data['artist'], album_data['album_title'])

    # Open the txt file
    with open(file, 'r', encoding='utf-8') as f:
        # Read the contents of the file
        contents = f.read()

    # Define the lines we want to modify and the new content to replace them with
    lines_to_modify = [
        ' | levy              = ',
        ' | artisti           = ',
        ' | julkaistu         = ',
        ' | minuutit          = ',
        ' | sekunnit          = ',
        ' | edellinen         = ',
        ' | vuosie            = ',
    ]

    new_content = [
        album_data['album_title'],
        album_data['artist'],
        album_data['full_date'],
        str(album_data['total_min']),
        str(album_data['total_sec']).zfill(2),
        previous_album['title'] if previous_album else '',
        previous_album['year'] if previous_album else ''
    ]

    # Loop through each line, replace with the new content, and update the contents variable
    for i, line_to_modify in enumerate(lines_to_modify):
        if 'artisti' in line_to_modify or 'edellinen' in line_to_modify:
            contents = contents.replace(line_to_modify, f'{line_to_modify}[[{new_content[i]}]]')
        else:
            contents = contents.replace(line_to_modify, f'{line_to_modify}{new_content[i]}')

    # Write the modified contents back to the file
    with open(file, 'w', encoding='utf-8') as f:
        f.write(contents)

    return [file, album_data]

def fill_tracklist(url_id, file_and_album):
    """Function that writes the track list information to the file

    Args:
        url_id (string): The last part of the Tidal browse album URL
        file_and_album (list): File path and album data
    """

    # Grab tracklist
    tracks_url = f'https://openapi.tidal.com/albums/{url_id}/items?countryCode=US&offset=0&limit=30'

    tracklist = get_tracklist(tracks_url)

    file = file_and_album[0]
    album_data = file_and_album[1]

    # Append the start of the tracklist module to the file
    with open(file, 'a', encoding='utf-8') as f:
        f.write('\n== Kappaleet ==')
        f.write('\n{{Kappalelista')
        f.write(f'\n | kokonaiskesto    = {album_data["total_min"]}.{album_data["total_sec"]:02d}')

    # Then the actual tracks one by one
    for track in tracklist:
        with open(file, 'a', encoding='utf-8') as fd:
            # Format the track duration string with leading zero for single-digit seconds
            track_duration = f'{track["track_minutes"]}.{track["track_seconds"]:02d}'
            fd.write(f'\n | nimi{track["track_number"]}           = {track["track_title"]}')
            fd.write(f'\n | huom{track["track_number"]}           = ')
            fd.write(f'\n | pituus{track["track_number"]}         = {track_duration}')
            fd.write('\n')

    # Add closing curly braces for the tracklist part of the template
    with open(file, 'a', encoding='utf-8') as f:
        f.write('}}\n')

def fill_lineup(file_and_album):
    """Function that writes lineup parts to the output file if available

    Args:
        file_and_album (list): File path and album data
    """

    # Add lineup parts
    file = file_and_album[0]

    with open(file, 'a', encoding='utf-8') as f:
        f.write('\n== Kokoonpano ==')

    # Read lineup from file if it exists, then write the information to template
    # NOTE! This assumes a format of Firstname Lastname - instrument, instrument, instrument

    if os.path.isfile('./lineup.txt'):
        with open('lineup.txt', 'r', encoding='utf-8') as f:
            lineup = [line.strip() for line in f]

        # Make lineup a dict
        band_dict = [{'Artist': artist_instrument[0].strip(), \
                      'Instruments': artist_instrument[1].strip()} \
                        for artist_instrument in [artist.split('-') for artist in lineup]]

        with open(list[0], 'a', encoding='utf-8') as f:
            f.write('\n')
            for artist in band_dict:
                artist_str = f"[[{artist['Artist']}]]"
                instruments_str_list = [inst.strip() for inst in artist['Instruments'].split(',')]
                instruments_str = ''
                if len(instruments_str_list) == 1:
                    instruments_str = f'[[{instruments_str_list[0]}]]'
                else:
                    for instrument in instruments_str_list:
                        instruments_str = instruments_str + f"[[{instrument}]], "
                    instruments_str = instruments_str[:-2]
                f.write('* ' + artist_str + ' - ' + instruments_str + '\n')

def add_reviews(reviews, file_and_album):
    file = file_and_album[0]

    with open(file, 'a', encoding='utf-8') as f:
        f.write('\n')
        f.write('== Arvostelut ==\n')

    for review in reviews:
        r = get_review(review)
        with open(file, 'a', encoding='utf-8') as f:
            f.write(r + '\n')


def get_reviews():
    reviews = []

    while True:
        review_url = input("Enter an URL to a review for the album (just press enter to end): ")

        if not review_url:
            return reviews

        reviews.append(review_url)
