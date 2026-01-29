import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from html.parser import HTMLParser


BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            for k, v in attrs:
                if k.lower() == "href":
                    self.links.append(v)


def get_links(url: str) -> list[str]:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    parser = LinkParser()
    parser.feed(resp.text)
    return parser.links


def get_latest_zip_urls(base_url: str, n: int = 3) -> list[str]:
    year_dirs = [l for l in get_links(base_url) if re.fullmatch(r"\d{4}/", l)]
    year_dirs.sort(reverse=True)

    quarters = []
    for year in year_dirs:
        year_url = urljoin(base_url, year)
        for link in get_links(year_url):
            if link.lower().endswith(".zip"):
                quarters.append(urljoin(year_url, link))

    return quarters[:n]


def download_zips(urls: list[str], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for url in urls:
        filename = url.split("/")[-1]
        path = out_dir / filename
        if path.exists():
            continue
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
