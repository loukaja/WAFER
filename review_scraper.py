import sys
from urllib.parse import urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import constants as c

def get_domain(review_url):
    parsed_url = urlparse(review_url)
    domain = parsed_url.netloc
    return domain

def get_review(review_url):
    domain = get_domain(review_url)
    try:
        response = requests.get(url=review_url, timeout=(3, 5))
        soup = BeautifulSoup(response.text, 'html.parser')
        if domain == 'kaaoszine.fi':
            review = get_kaaoszine_review(soup, review_url)
        elif domain == 'www.soundi.fi':
            review = get_soundi_review(soup, review_url)
        elif domain == 'metalliluola.fi':
            review = get_metalliluola_review(soup, review_url)
        elif domain == 'blabbermouth.net':
            review = get_blabbermouth_review(soup, review_url)
    except requests.exceptions.Timeout:
        sys.exit("The request timed out")
    except requests.exceptions.RequestException as e:
        sys.exit("An error occurred:", e)

    return review

def create_album_rating(review):
    if review['domain'] == 'kaaoszine.fi' or review['domain'] == 'blabbermouth.net' or review['domain'] == 'metalliluola.fi':
        site = review['domain'].split('.')[0].title()
    elif review['domain'] == 'www.soundi.fi':
        site = review['domain'].split('.')[1].title()
    rating = f"* [[{site}]]: {{{{Arvostelutähdet|{review['rating']}|{review['max_rating']}}}}}"
    reference = create_reference(review)
    rating = rating + reference
    return rating

def create_reference(review):
    current_date = datetime.now().strftime("%d.%m.%Y")
    # Remove leading zeros from day and month
    current_date = current_date.replace('.0', '.').lstrip('0')

    if review['domain'] != 'blabbermouth.net':
        reference = (f"<ref>{{{{Verkkoviite | Osoite = {review['url']} | Nimeke = {review['title']}"
                 f" | Tekijä = {review['author']} | Sivusto = {review['domain']} | "
                 f"Ajankohta = {review['date']} | Viitattu = {current_date} }}}}</ref>")
    else:
        reference = (f"<ref>{{{{Verkkoviite | Osoite = {review['url']} | Nimeke = {review['title']}"
                    f" | Tekijä = {review['author']} | Sivusto = {review['domain']} | "
                    f"Ajankohta = | Viitattu = {current_date} | Kieli = {{{{en}}}} }}}}</ref>")

    return reference

def get_kaaoszine_review(soup, review_url):

    domain = 'kaaoszine.fi'

    title = soup.find(class_='article-title').get_text()

    # Initialize a variable to hold the rating
    rating = 0
    max_rating = 5

    # Find the <div> element with class="rating"
    rating_div = soup.find('div', class_='rating')

    # Find all <div> elements within the rating_div
    divs = rating_div.find_all('div')

    # Loop through each <div> element
    for div in divs:
        # Check if the div has class="one"
        if 'one' in div.get('class', []):
            # Increment the rating by 1
            rating += 1
        elif 'half' in div.get('class', []):
            # Increment the rating by 1
            rating += 0.5

    # Find the <div> element with class="author-and-date"
    author_and_date_div = soup.find('div', class_='author-and-date')

    # Extract the author name (inside the strong tags)
    author_name = author_and_date_div.find('strong').get_text()

    # Extract the date (after the dash)
    date_str = author_and_date_div.get_text().split('-')[-1].strip()

    review = {
        "title": title,
        "author": author_name,
        "date": date_str,
        "rating": rating,
        "max_rating": max_rating,
        "url": review_url,
        "domain": domain
    }

    album_rating = create_album_rating(review)

    return album_rating

def get_soundi_review(soup, review_url):
    domain = 'www.soundi.fi'
    title = soup.find('h1').get_text()
    max_rating = 5

    # Find out the rating by counting amount of li tags
    div = soup.find('div', class_='pb-2 flex pt-2 justify-center')

    ratings = div.find_all('li')

    rating = len(ratings)

    # Locate credits and release date
    credit = soup.find('div', class_='flex w-full overflow-hidden mb-6 pb-3 text-xs px-2 sm:px-0')

    divs = credit.find_all('div')

    author_name = divs[1].get_text().split(':')[1].strip()[:-1]
    release_date = divs[0].get_text().split()[-1][:-1]
    month = release_date.split('/')[0]
    year = release_date.split('/')[1]

    date_str = c.KK_BASE[int(month)] + ' ' + year

    review = {
            "title": title,
            "author": author_name,
            "date": date_str,
            "rating": rating,
            "max_rating": max_rating,
            "url": review_url,
            "domain": domain
        }

    album_rating = create_album_rating(review)

    return album_rating

def get_metalliluola_review(soup, review_url):
    domain = 'metalliluola.fi'

    title = soup.find('h1').get_text()

    author_div = soup.find('div', class_='td-post-author-name')
    author_name = author_div.a.get_text()

    date = soup.find('time', class_='entry-date updated td-module-date').get_text()

    rating = soup.find('h3').get_text()
    rating = rating.split('/')[0].strip()
    max_rating = 10

    review = {
            "title": title,
            "author": author_name,
            "date": date,
            "rating": rating,
            "max_rating": max_rating,
            "url": review_url,
            "domain": domain
        }

    album_rating = create_album_rating(review)

    return album_rating

def get_blabbermouth_review(soup, review_url):
    domain = 'blabbermouth.net'
    artist = soup.find('h1', class_='margin__top-default margin__bottom-default').get_text()
    album = soup.find('h2', class_='margin__bottom-default').get_text()

    title = artist + ' - ' + album

    # Get rating
    rating_div = soup.find('div', class_='reviews-rate-comments')

    if rating_div:
        rating = rating_div.find('div').get_text().split('/')[0].strip()
    else:
        rating = None
    max_rating = 10

    # Find the div containing the author's name
    author_div = soup.find('div', class_='news-relative-items').find('div')

    # Extract the author's name from the text within the div
    author_name = author_div.get_text(strip=True).replace('Author:', '')

    review = {
            "title": title,
            "author": author_name,
            "date": 'Unavailable',
            "rating": rating,
            "max_rating": max_rating,
            "url": review_url,
            "domain": domain
        }

    album_rating = create_album_rating(review)

    return album_rating

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python script.py <review_url>")
        sys.exit(1)

    url = sys.argv[1]

    print(get_review(url))
