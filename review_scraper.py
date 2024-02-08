import sys
from urllib.parse import urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_domain(review_url):
    parsed_url = urlparse(review_url)
    domain = parsed_url.netloc
    return domain

def get_review(review_url):
    domain = get_domain(review_url)

    try:
        response = requests.get(url=review_url, timeout=(3, 5))
        soup = BeautifulSoup(response.text, 'html.parser')

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
    except requests.exceptions.Timeout:
        sys.exit("The request timed out")
    except requests.exceptions.RequestException as e:
        sys.exit("An error occurred:", e)

    return album_rating

def create_album_rating(review):
    site = review['domain'].split('.')[0].title()
    rating = f"* [[{site}]]: {{{{Arvostelutähdet|{review['rating']}|{review['max_rating']}}}}}"
    reference = create_reference(review)
    rating = rating + reference
    return rating

def create_reference(review):
    current_date = datetime.now().strftime("%d.%m.%Y")
    # Remove leading zeros from day and month
    current_date = current_date.replace('.0', '.').lstrip('0')
    reference = (f"<ref>{{{{Verkkoviite | Osoite = {review['url']} | Nimeke = {review['title']} | "
                 f"Tekijä = {review['author']} | Sivusto = {review['domain']} | "
                 f"Ajankohta = {review['date']} | Viitattu = {current_date} }}}}</ref>")
    return reference

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python script.py <review_url>")
        sys.exit(1)

    url = sys.argv[1]

    print(get_review(url))
