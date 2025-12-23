'''
este módulo serve como a configuração geral do scrapper, todas as seeds, dominios permitidos e tal, estão aqui
'''

from pathlib import Path

SEEDS = [
    "https://www.gov.br/previc/pt-br",
    "https://sisconp.previc.gov.br/"
]

DOMAIN_ALLOW = ["gov.br", "previc.gov.br", "sisconp.previc.gov.br"]

FILE_EXTENSIONS = (".zip", ".pdf", ".csv", ".xls", ".xlsx", ".doc", ".docx")

HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"), 
           "Accept": "application/pdf, application/octet-stream, /", "Accept-Language": "pt-BR, pt;q=0.9", "Connection": "keep-alive",}

REQUEST_DELAY = 0.4 # segundos entre as requisições

OUT_BASE = Path("data/previc") # diretório base para salvar os dados