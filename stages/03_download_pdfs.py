import json
import time
import pathlib
import requests

from tqdm import tqdm

cachedir = pathlib.Path('./cache')
brickdir = pathlib.Path('./brick') / 'cir_reports.pdf'
brickdir.mkdir(parents=True, exist_ok=True)

# DOWNLOAD PDFS ================================================================
all_pdf_links = json.load(open(cachedir / 'all_pdf_links.json'))

mkpdfpath = lambda pdf_link: (brickdir / pdf_link.split('id=')[-1]).with_suffix('.pdf')
new_pdf_links = [pdf_link for pdf_link in all_pdf_links if not mkpdfpath(pdf_link).exists()]

for pdf_link in tqdm(new_pdf_links):
    pdf_path = (brickdir / pdf_link.split('id=')[-1]).with_suffix('.pdf')
    res = requests.get(pdf_link)
    res.raise_for_status()
    time.sleep(0.1)
    _ = pdf_path.write_bytes(res.content)