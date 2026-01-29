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
    years = []
    for link in get_links(base_url):
        clean = link.split("?")[0].strip("/")
        if re.fullmatch(r"\d{4}", clean):
            years.append(clean + "/")
    years = sorted(set(years), reverse=True)

    grupos: dict[tuple[int, int], list[str]] = {}

    for y in years:
        year_url = urljoin(base_url, y)
        for link in get_links(year_url):
            name = link.split("?")[0]
            if not name.lower().endswith(".zip"):
                continue

            m = re.search(r"([1-4])T(20\d{2})", name)
            if not m:
                continue

            tri = int(m.group(1))
            ano = int(m.group(2))
            grupos.setdefault((ano, tri), []).append(urljoin(year_url, name))

    ultimos = sorted(grupos.keys(), reverse=True)[:n]

    urls = []
    for t in ultimos:
        urls.extend(sorted(grupos[t]))
    return urls


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
