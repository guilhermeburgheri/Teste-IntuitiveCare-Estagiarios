from pathlib import Path
from ans_dados.ans_source import get_latest_zip_urls, download_zips, BASE_URL

def main():
    urls = get_latest_zip_urls(BASE_URL)
    download_zips(urls, Path(".documentos/zips"))
    print("Download finalizado.")

if __name__ == "__main__":
    main()
