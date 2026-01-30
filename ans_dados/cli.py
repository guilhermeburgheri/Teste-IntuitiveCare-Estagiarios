from pathlib import Path
from ans_dados.ans_source import get_latest_zip_urls, download_zips, BASE_URL
from ans_dados.processa_dados import extrair_zips, contar_arquivos_com_eventos
from ans_dados.consolida_dados import gerar_finalizado, zipar_finalizado


def main():
    zips_dir = Path(".documentos/zips")
    extracao_dir = Path(".documentos/extracao")
    cons_dir = Path(".documentos/filtrado")

    # 1.1
    urls = get_latest_zip_urls(BASE_URL)
    download_zips(urls, zips_dir)

    # 1.2
    extrair_zips(zips_dir, extracao_dir)
    total = contar_arquivos_com_eventos(extracao_dir)

    # 1.3
    finalizado = gerar_finalizado(extracao_dir, cons_dir)
    zipar_finalizado(finalizado, Path("consolidado_despesas.zip"))
    
    print(f"Processamento finalizado. Arquivos válidos: {total}")
    print(f"Arquivo gerado: consolidado_despesas.zip")

if __name__ == "__main__":
    main()
