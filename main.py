'''
o player de todos os módulos, ele que vai orquestrar o funcionamento do crawler, downloader e armazenamento dos arquivos baixados
'''

import requests
from config import SEEDS_FULL, SEEDS_FOCUSED, OUT_BASE, HEADERS
from state import State
from downloader import download
from discovery import crawl
from storage import append_index
from logger import setup_logger

def main():
    MODE = "focused" # "full" ou "focused"
    logger.info(f"Modo de execução: {MODE.upper()}")

    seeds = SEEDS_FULL if MODE == "full" else SEEDS_FOCUSED

    session = requests.Session()
    session.headers.update(HEADERS)

    OUT_BASE.mkdir(parents=True, exist_ok=True)
    state = State(OUT_BASE)

    logger = setup_logger(OUT_BASE / "logs")
    logger.info("Iniciando o crawler...")

    crawl(
        session=session,
        seeds=seeds,
        state=state,
        downloader=download,
        storage=append_index,
        out_base=OUT_BASE,
        logger=logger,
        mode = MODE
    )
    logger.info("Scraper finalizado")

if __name__ == "__main__":
    main()