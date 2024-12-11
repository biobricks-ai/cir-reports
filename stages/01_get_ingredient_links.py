
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from tqdm import tqdm

from tenacity import retry, stop_after_attempt, wait_exponential
import time
import json
import pathlib
import subprocess


cachedir = pathlib.Path('./cache') 
cachedir.mkdir(parents=True, exist_ok=True)

# USE SELENIUM TO SCRAPE INGREDIENT PAGE LINKS =================================
options = Options()
options.add_argument("--headless --disable-gpu --no-sandbox --disable-dev-shm-usage")
subprocess.run("docker rm -f selenium-chrome", shell=True)
subprocess.run("docker run --name selenium-chrome -d -p 4444:4444 --shm-size=2g selenium/standalone-chrome", shell=True)
time.sleep(10)
driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=options)
wait = WebDriverWait(driver, 10)

# URL of the page to scrape
base_url = "https://cir-reports.cir-safety.org"
driver.get(base_url)

# Extract links from the page
elements = driver.find_elements(By.TAG_NAME, "a")
jslinks = [elem.text for elem in elements if elem.get_attribute('href') == f'{base_url}/#']

print(f"Number of jslinks: {len(jslinks)}")
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
def get_page_links(link_text):
    try:
        refreshed_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
        refreshed_link.click()
        time.sleep(0.5)  # Ensure page transition completes
        page_links = driver.find_elements(By.TAG_NAME, "a")
        page_links = [pl for pl in page_links if 'cir-ingredient-status-report' in pl.get_attribute('href')]
        hrefs = [pl.get_attribute('href') for pl in page_links]
        return hrefs
    except StaleElementReferenceException:
        driver.refresh()
        return get_page_links(link_text)

all_ingredient_page_links = set()
for link_text in tqdm(jslinks):
    ingredient_page_links = get_page_links(link_text)
    all_ingredient_page_links.update(ingredient_page_links)

driver.quit()

outpath = cachedir / 'ingredient_page_links.json'
json.dump(list(all_ingredient_page_links), open(outpath, 'w'))

# TEST RESULT =====================================================================
res = json.load(open(outpath))
assert len(res) > 1000
assert len(res) == len(set(res))

