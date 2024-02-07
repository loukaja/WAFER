"""Main module to be run
"""

import sys
import time

from helpers import fill_album_info_box, fill_tracklist, fill_lineup

def run(link):
    """Main function to be run

    Args:
        link (string): Tidal album link, for example: 'https://tidal.com/browse/album/102314585'
    """

    # Grab the ID from the album link
    url_id = link.split('/')[-1]

    file_and_album = fill_album_info_box(url_id)

    # Sleep for a second so we don't hammer the API too often
    time.sleep(1)

    fill_tracklist(url_id, file_and_album)

    fill_lineup(file_and_album)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py https://tidal.com/browse/album/<album_id>")
        sys.exit(1)

    album_link = sys.argv[1]
    run(album_link)
