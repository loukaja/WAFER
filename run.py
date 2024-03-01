"""Main module to be run
"""

import time

from helpers import fill_album_info_box, fill_tracklist, fill_lineup, get_reviews, add_reviews, add_external_links, add_references, export_wiki_template, add_stub, add_classes


def run(album_info):
    """Main function to be run

    Args:
        link (string): Tidal album link, for example: 'https://tidal.com/browse/album/102314585'
    """

    file, album = fill_album_info_box(album_info)

    # Sleep for a second so we don't hammer the API too often
    time.sleep(1)

    fill_tracklist(album_info['link'], file, album)

    fill_lineup(file, album_info['members'])

    if album_info['reviews']:
        review_list = get_reviews(album_info['reviews'])

        add_reviews(review_list, file)

    # Delete entries without URL's before attempting to add the links
    for i in range(len(album_info['external_links']) - 1, -1, -1):
        if not album_info['external_links'][i]['url']:
            del album_info['external_links'][i]

    add_references(file)

    add_external_links(album_info['external_links'], file, album)

    if album_info['stub']:
        add_stub(file)

    add_classes(file, album_info['classes'])

    wiki_template = export_wiki_template(file)

    return wiki_template
