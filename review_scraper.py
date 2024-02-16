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

    if domain not in c.SUPPORTED_DOMAINS:
        return None

    try:
        response = requests.get(url=review_url, timeout=(3, 5))
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.Timeout:
        sys.exit("The request timed out")
    except requests.exceptions.RequestException as e:
        sys.exit("An error occurred:", e)

    title = get_review_title(soup, domain)
    author = get_review_author(soup, domain)
    date = get_review_date(soup, domain)
    rating = get_review_rating(soup, domain)

    review = {
        "title": title,
        "author": author,
        "date": date,
        "rating": rating,
        "url": review_url,
        "domain": domain
    }

    rating = create_album_rating(review)
    reference = create_reference(review)

    if rating and reference:
        rating_and_reference = rating + reference

        return rating_and_reference

    return None


def create_album_rating(review):
    split_domain = review['domain'].split('.')
    if split_domain[0] == 'metalinjection':
        site = 'Metal Injection'
    else:
        site = split_domain[0].title() if len(
            split_domain) == 2 else split_domain[1].title()

    max_rating = 5 if review['domain'] in [
        'kaaoszine.fi', 'www.soundi.fi'] else 10
    if not review['rating']:
        return None
    rating = f"* [[{site}]]: {{{{Arvostelutähdet|{review['rating']}|{max_rating}}}}}"
    return rating


def get_review_title(soup, domain):
    if domain == 'kaaoszine.fi':
        title = soup.find(class_='article-title').get_text()
    elif domain == 'www.soundi.fi':
        title = soup.find('h1').get_text()
    elif domain == 'metalliluola.fi':
        title = soup.find('h1').get_text()
    elif domain == 'blabbermouth.net':
        artist = soup.find(
            'h1', class_='margin__top-default margin__bottom-default').get_text()
        album = soup.find('h2', class_='margin__bottom-default').get_text()
        title = artist + ' - ' + album
    elif domain == 'metalinjection.net':
        title = soup.find('h1').get_text()
    elif domain == 'www.metalsucks.net':
        title = soup.find('h1').get_text()

    return title


def get_review_author(soup, domain):
    if domain == 'kaaoszine.fi':
        author_and_date_div = soup.find('div', class_='author-and-date')
        author = author_and_date_div.find('strong').get_text()
    elif domain == 'www.soundi.fi':
        date_and_author = soup.find_all('div', class_='text-gray-400')
        author = date_and_author[1].get_text().split(':')[1].strip()[:-1]
    elif domain == 'metalliluola.fi':
        author_div = soup.find('div', class_='td-post-author-name')
        author = author_div.a.get_text()
    elif domain == 'blabbermouth.net':
        author_div = soup.find('div', class_='news-relative-items').find('div')
        author = author_div.get_text(strip=True).replace('Author:', '')
    elif domain == 'metalinjection.net':
        author_span = soup.find('span', class_='zox-author-name')
        author = author_span.find('a').get_text()
    elif domain == 'www.metalsucks.net':
        author = soup.find('span', class_='author').find('a').get_text()

    return author


def get_review_date(soup, domain):
    if domain == 'kaaoszine.fi':
        author_and_date_div = soup.find('div', class_='author-and-date')
        date = author_and_date_div.get_text().split('-')[-1].strip()
    elif domain == 'www.soundi.fi':
        date_and_author = soup.find_all('div', class_='text-gray-400')
        release_date = date_and_author[0].get_text().split()[-1][:-1]
        month, year = release_date.split('/')
        date = c.KK_BASE[int(month)] + ' ' + year
    elif domain == 'metalliluola.fi':
        date = soup.find(
            'time', class_='entry-date updated td-module-date').get_text()
    elif domain == 'blabbermouth.net':
        date = 'Unavailable'
    elif domain == 'metalinjection.net':
        date_time = soup.find('time')['datetime']
        date = datetime.strptime(date_time, '%Y-%m-%d').strftime('%#d.%#m.%Y')
    elif domain == 'www.metalsucks.net':
        date_time = soup.find('time')['datetime']
        date = datetime.strptime(date_time, '%Y-%m-%d').strftime('%#d.%#m.%Y')

    return date


def get_review_rating(soup, domain):
    if domain == 'kaaoszine.fi':
        rating_div = soup.find(class_='rating')
        one_count = len(rating_div.find_all(class_='one'))
        half_count = len(rating_div.find_all(class_='half'))
        rating = one_count + 0.5 * half_count
    elif domain == 'www.soundi.fi':
        div = soup.find('div', class_='pb-2 flex pt-2 justify-center')
        ratings = div.find_all('li')
        rating = len(ratings)
    elif domain == 'metalliluola.fi':
        rating = soup.find('h3').get_text()
        rating = rating.split('/')[0].strip()
    elif domain == 'blabbermouth.net':
        rating_div = soup.find('div', class_='reviews-rate-comments')
        rating = rating_div.find('div').get_text().split(
            '/')[0].strip() if rating_div else None
    elif domain == 'metalinjection.net':
        rating_span = soup.find(
            'span', class_='rwp-overlall-score-value')
        rating = rating_span.get_text() if rating_span else None
    elif domain == 'www.metalsucks.net':
        img_tag = soup.find('div', class_='rating').find('img')
        src_value = img_tag['src']
        rating = src_value.split('/')[-1].split('.')[0].split('-')[1]
        if rating[1] == 5:
            rating = int(rating) / 10
        else:
            rating = int(int(rating) / 10)

    return rating


def create_reference(review):
    current_date = datetime.now().strftime("%d.%m.%Y")
    # Remove leading zeros from day and month
    current_date = current_date.replace('.0', '.').lstrip('0')
    domain = review['domain']

    language = " | Kieli = {{en}}" if domain == 'blabbermouth.net' or domain == 'metalinjection.net' else ""
    date = "Ajankohta =" if domain == 'blabbermouth.net' else f"Ajankohta = {review['date']}"

    reference = (f"<ref>{{{{Verkkoviite | Osoite = {review['url']} | Nimeke = {review['title']}"
                 f" | Tekijä = {review['author']} | Sivusto = {domain} | "
                 f"{date} | Viitattu = {current_date}{language} }}}}</ref>")

    return reference


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python script.py <review_url>")
        sys.exit(1)

    url = sys.argv[1]

    print(get_review(url))
