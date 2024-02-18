"""Main module to be run
"""

import time

from helpers import fill_album_info_box, fill_tracklist, fill_lineup, get_reviews, add_reviews, add_external_links, add_references, export_wiki_template, add_stub


def run(link, reviews, members, external_links, stub, toc):
    """Main function to be run

    Args:
        link (string): Tidal album link, for example: 'https://tidal.com/browse/album/102314585'
    """

    # Grab the ID from the album link
    url_id = link.split('/')[-1]

    file_and_album = fill_album_info_box(url_id, toc)

    # Sleep for a second so we don't hammer the API too often
    time.sleep(1)

    fill_tracklist(url_id, file_and_album)

    fill_lineup(file_and_album, members)

    if reviews:
        review_list = get_reviews(reviews)

        add_reviews(review_list, file_and_album)

    # Delete entries without URL's before attempting to add the links
    for i in range(len(external_links) - 1, -1, -1):
        if not external_links[i]['url']:
            del external_links[i]

    add_references(file_and_album)

    add_external_links(external_links, file_and_album)

    if stub:
        add_stub(file_and_album)

    wiki_template = export_wiki_template(file_and_album)

    return wiki_template
