import sys
sys.path.append('./stages')

import re
import time
import json
import pathlib
import requests

from utils.simple_cache import simple_cache
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential

cachedir = pathlib.Path('./cache')

# GET PDF LINKS ================================================================
ingredient_page_links = json.load(open(cachedir / 'ingredient_page_links.json'))
base_url = "https://cir-reports.cir-safety.org"

# cache for 2 days
simple_cache_dir = cachedir / 'simple_cache'
simple_cache_dir.mkdir(parents=True, exist_ok=True)

@simple_cache(simple_cache_dir.as_posix(), expiry_seconds=60*60*48)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
def download_pdfs_from_ingredient_page(ingredient_page_link):
    # response = scraperapi.scrape(ingredient_page_link, ultra_premium=True)
    response = requests.get(ingredient_page_link)
    response.raise_for_status()
    time.sleep(0.5)

    pattern = r'/view-attachment\?id=[^"\']+'
    pdf_links = [match.group() for match in re.finditer(pattern, response.text)]
    return [f"{base_url}/{pdf_link}" for pdf_link in pdf_links]
    
all_pdf_links = []
for ingredient_page_link in tqdm(ingredient_page_links):
    try:
        pdf_links = download_pdfs_from_ingredient_page(ingredient_page_link)
        all_pdf_links.extend(pdf_links)
    except Exception as e:
        print(f"Error downloading {ingredient_page_link}: {e}")
        continue

# write all_pdf_links to cache/all_pdf_links.txt
all_pdf_links = list(set(all_pdf_links))
json.dump(all_pdf_links, open(cachedir / 'all_pdf_links.json', 'w'))

# TEST RESULT =====================================================================
res = json.load(open(cachedir / 'all_pdf_links.json'))
assert len(res) > 1000
assert len(res) == len(set(res))

