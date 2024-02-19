# Google Flights -> Outline Scraper

This is a small utility I hacked together to help me and friends plan trips.

It scrapes the Google Flights website and returns a list of flights and their prices.

Then it uploads that data to my personal outline server via the API.

It's a bit slow and janky, but it works :)

You'll need to make sure you're running this with a framebuffer of some kind (xvfb works) for *some reason* ¯\\_(ツ)_/¯

You'll also need a .env file with the following variables:

- WIKI_API_KEY (your outline wiki API key)
- PAGE_ID (the ID of the page you want to upload to)
- WIKI_URL (the URL of your outline wiki)

This script is also hard-coded for specific routes and dates (PAX Aus 2024) so you'll need to change that if you want to use it for something else.
