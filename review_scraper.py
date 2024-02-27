import sys
from urllib.parse import urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import constants as c
import platform
import re
from fake_useragent import UserAgent


def get_domain(review_url):
    parsed_url = urlparse(review_url)
    domain = parsed_url.netloc
    return domain


def get_review(review_url):
    domain = get_domain(review_url)
    ua = UserAgent()
    headers = {'user-agent': f'{ua.random}'}

    if domain not in c.SUPPORTED_DOMAINS:
        return None

    try:
        response = requests.get(url=review_url, headers=headers, timeout=(3, 5))
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
    
    if site == 'Angrymetalguy':
        site = 'Angry Metal Guy'
    elif site == 'Distortedsoundmag':
        site = 'Distorted Sound Magazine'
    elif site == 'Loudersound':
        site = 'Metal Hammer'

    max_5 = ['kaaoszine.fi', 'www.soundi.fi', 'www.inferno.fi', 'www.metalsucks.net',
             'www.angrymetalguy.com', 'www.loudersound.com']

    max_rating = 5 if review['domain'] in max_5 else 10
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
    elif domain == 'www.inferno.fi':
        title = soup.find('h1').get_text()
    elif domain == 'www.angrymetalguy.com':
        title = soup.find('title').get_text()
        title = title.split('Review')[0].strip()
    elif domain == 'distortedsoundmag.com':
        title = ' - '.join([item.strip().title() for item in soup.find('title').get_text().split('-')[:2]])
    elif domain == 'www.loudersound.com':
        title = soup.find('title').get_text().split('|')[0]

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
    elif domain == 'www.inferno.fi':
        author = soup.find('a', {'rel': 'author'}).get_text()
    elif domain == 'www.angrymetalguy.com':
        author = soup.find('span', class_='uppercase authorname').get_text()
        author = author.title()
    elif domain == 'distortedsoundmag.com':
        author_span = soup.find('span', class_='cm-author cm-vcard')
        author = author_span.find('a').get_text()
    elif domain == 'www.loudersound.com':
        author_span = soup.find('span', class_='author-byline__author-name')
        author = author_span.find('a').get_text()

    # If "real" name, try to split is so we can have it in Lastname, Firstname format
    if domain != 'www.angrymetalguy.com':
        split = author.split()
        author = f"{split[1]}, {split[0]}"

    return author


def get_review_date(soup, domain):
    if domain == 'www.inferno.fi':
        date = soup.find('div', class_='pr-2 pl-1 text-gray-400').get_text()
    else:
        meta_tag = soup.find('meta', property='article:published_time')
        dt = meta_tag['content']
        dt = dt.split('T')[0]
        date = convert_date(dt)

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
    elif domain == 'www.inferno.fi':
        img_tag = soup.find('div', class_='review-rating').find('img')
        lazy_src_url = img_tag['data-lazy-src']
        rating = lazy_src_url.split('/')[-1].split('.')[0]
        if '-' in rating:
            rating = rating.replace('-', '.')
    elif domain == 'www.angrymetalguy.com':
        rating_text = soup.find('strong', string=re.compile('^Rating'))
        rating = rating_text.next_sibling.strip()

        if rating[0] == ':':
            rating = rating.split(':')[1].split('/')[0].strip()
        else:
            rating = rating.split('/')[0].strip()
    elif domain == 'distortedsoundmag.com':
        rating_b = soup.find('b', string=re.compile('^Rating'))

        if rating_b:
            rating = rating_b.next_sibling.get_text().split('/')[0]
        else:
            rating = soup.find('strong', string=re.compile('^Rating')).get_text().split()[1].split('/')[0]
    elif domain == 'www.loudersound.com':
        rating_span = soup.find('span', class_='chunk rating')
        rating = rating_span.get('aria-label')
        rating = re.findall(r'\d+', rating)[0]

    return rating


def create_reference(review):
    current_date = datetime.now().strftime("%d.%m.%Y")
    # Remove leading zeros from day and month
    current_date = current_date.replace('.0', '.').lstrip('0')
    domain = review['domain']
    english = ['blabbermouth.net', 'metalinjection.net', 'www.metalsucks.net',
               'www.angrymetalguy.com', 'distortedsoundmag.com', 'www.loudersound.com']

    language = " | Kieli = {{en}}" if domain in english else ""
    date = f"Ajankohta = {review['date']}"

    reference = (f"<ref>{{{{Verkkoviite | Osoite = {review['url']} | Nimeke = {review['title']}"
                 f" | Tekijä = {review['author']} | Sivusto = {domain} | "
                 f"{date} | Viitattu = {current_date}{language} }}}}</ref>")

    return reference


def convert_date(date):
    if platform.system() == 'Windows':
        return datetime.strptime(date, '%Y-%m-%d').strftime('%#d.%#m.%Y')
    return datetime.strptime(date, '%Y-%m-%d').strftime('%-d.%-m.%Y')


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python script.py <review_url>")
        sys.exit(1)

    url = sys.argv[1]

    print(get_review(url))
