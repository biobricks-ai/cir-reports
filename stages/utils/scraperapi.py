import os, requests, re, sqlite3, boto3, json, pathlib, dotenv

dotenv.load_dotenv()
scraperapi_key = os.getenv('SCRAPER_API')

def scrape(scrape_url, autoparse=False, binary=False, ultra_premium=False):
    params = {
        'api_key': scraperapi_key,
        'url': scrape_url,
        'autoparse': autoparse,
        'binary_target': binary,
        'ultra_premium': ultra_premium
    }
    return requests.get('http://api.scraperapi.com', params=params)
