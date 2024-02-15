# WAFER

Simplifying wikipedia album page creation since 2024. Powered by Tidal.

## What is WAFER and why should I care?

WAFER is short for Wikipedia-Album-FormattER. Basically, it's a form you fill
in with a link to album, possibly some links to reviews, band lineup etc. Then
you press the Generate button, and it will create a basic skeleton for your album
page.

## How does it work?
The frontend is done with Streamlit. Backend is pure Python. Album information
is pulled from Tidal by using their API. Review data is pulled from each page
using Requests and BeautifulSoup. Bit by bit, the information is then entered
into a txt file on your computer.

## How do I use it?
- Clone the project
- Create virtual environment and activate it
- Install required packages by running 'pip install -r requirements.txt'
- Open your terminal of choice, and navigate to your project folder
- Run 'streamlit run app.py' and wait for your browser to open the form page

## Anything else I need to know?
The app uses a Finnish wiki template and it only supports Finnish for now. I'm
planning on adding support for other languages eventually, once I get all the
features working. I wouldn't hold my breath, though. This might take a while.

I made it pretty forgiving, so even if you would add 10 review fields and only
fill one of them, the app will still work fine. Same goes for band members.
For instruments, the app supports entering multiple instruments in the same field,
you just need to split them using a comma, like so: 'Guitar, vocals'. The app
will take care of the rest and even make them into intra-wiki links for you.

As a bonus, review_scraper.py is actually possible to run by itself if you just
wish to get a review complete with score and reference. Just run it through the
command line, adding the link to the review as an argument.

## I want feature xyz!
Please open an issue, I'll see what I can do.
