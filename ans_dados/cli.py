from pathlib import Path
from ans_dados.ans_source import get_latest_zip_urls, download_zips, BASE_URL
from ans_dados.processa_dados import extrair_zips, contar_arquivos_com_eventos


def main():
    zips_dir = Path(".documentos/zips")
    extracao_dir = Path(".documentos/extracao")

    urls = get_latest_zip_urls(BASE_URL)
    download_zips(urls, zips_dir)

    extrair_zips(zips_dir, extracao_dir)

    total = contar_arquivos_com_eventos(extracao_dir)
    print(f"Processamento finalizado. Arquivos válidos: {total}")

if __name__ == "__main__":
    main()
