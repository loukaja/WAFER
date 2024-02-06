import requests
import time
from pprint import pprint
import json

import constants as c

from helpers import *

def run():

    # Hardcoded url for now, will be changed later
    url = 'https://openapi.tidal.com/albums/311501062?countryCode=US'

    # Get artist and album name, duration and release date
    album_data = get_release_information(url)

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
    ]

    new_content = [
        album_data['album_title'],
        album_data['artist'],
        album_data['full_date'],
        str(album_data['total_min']),
        str(album_data['total_sec']),
    ]

    # Loop through each line, replace with the new content, and update the contents variable
    for i, line_to_modify in enumerate(lines_to_modify):
        contents = contents.replace(line_to_modify, f'{line_to_modify}{new_content[i]}')

    # Write the modified contents back to the file
    with open(file, 'w', encoding='utf-8') as f:
        f.write(contents)

    # Sleep for a seoncd so we don't hammer the API too often
    time.sleep(1)

    # Grab tracklist
    tracks_url = 'https://openapi.tidal.com/albums/311501062/items?countryCode=US&offset=0&limit=10'

    tracklist = get_tracklist(tracks_url)

    # Append the start of the tracklist module to the file
    with open(file, 'a', encoding='utf-8') as f:
        f.write('\n== Kappaleet ==')
        f.write('\n{{Kappalelista')
        f.write(f'\n | kokonaiskesto    = {album_data["total_min"]}.{album_data["total_sec"]}')

    # Then the actual tracks one by one
    for track in tracklist:
        with open(file, 'a', encoding='utf-8') as fd:
            fd.write(f'\n | nimi{track["track_number"]}           = {track["track_title"]}')
            fd.write(f'\n | huom{track["track_number"]}           = ')
            fd.write(f'\n | pituus{track["track_number"]}         = {track["track_minutes"]}.{track["track_seconds"]}')
            fd.write('\n')

    # Add closing curly braces for the tracklist part of the template
    with open(file, 'a', encoding='utf-8') as f:
        f.write('}}\n')

    # Add lineup parts
    with open(file, 'a', encoding='utf-8') as f:
        f.write('\n== Kokoonpano ==')

    # Read lineup from file if it exists, then write the information to template
    # NOTE! This assumes a format of Firstname Lastname - instrument, instrument, instrument
        
    # TODO: Figure out a better way to get this information
    if os.path.isfile('./lineup.txt'):
        with open('lineup.txt', 'r', encoding='utf-8') as f:
            lineup = [line.strip() for line in f]

        # Make lineup a dict
        band_dict = [{'Artist': artist_instrument[0].strip(), 'Instruments': artist_instrument[1].strip()} for artist_instrument in [artist.split('-') for artist in lineup]]

        with open(file, 'a', encoding='utf-8') as f:
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

if __name__ == '__main__':
    run()