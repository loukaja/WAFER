import sys
import os
import time

from helpers import *

def run(album_link):

    # Grab the ID from the album link
    url_id = album_link.split('/')[-1]
    
    list = fill_album_info_box(url_id)

    # Sleep for a second so we don't hammer the API too often
    time.sleep(1)

    fill_tracklist(url_id, list) 

    fill_lineup(list)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py https://tidal.com/browse/album/<album_id>")
        sys.exit(1)
    
    album_link = sys.argv[1]
    run(album_link)