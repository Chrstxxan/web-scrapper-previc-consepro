"""
discovery para varrer o site PREVIC e trazer docs relevantes.
"""

import requests
import time
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# ============================
# Configurações
# ============================

SEEDS = [
    "https://www.gov.br/previc/pt-br",
    "https://sisconp.previc.gov.br/"
]

DOMAIN_ALLOW = ["gov.br", "previc.gov.br", "sisconp.previc.gov.br"]

FILE_EXTENSIONS = (".zip", ".pdf", ".csv", ".xls", ".xlsx", ".doc", ".docx")

PDF_KEYWORDS = ["invest", "previd", "fund", "efpc", "atuar",
                "estat", "dados", "carteira", "aloc", "rentab",
                "risco"]

OUT_BASE = Path("data/previc")

HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"), 
           "Accept": "application/pdf, application/octet-stream, /", "Accept-Language": "pt-BR, pt;q=0.9", "Connection": "keep-alive",}

REQUEST_DELAY = 0.4 # segundos entre as requisições

# ============================
# Funções auxiliares
# ============================

def sha1_bytes(b: bytes) -> str:
    # Retorna o hash SHA1 dos bytes fornecidos.
    return hashlib.sha1(b).hexdigest()

def is_internal(url: str) -> bool:
    # Verifica se a URL pertence aos domínios permitidos.
    netloc = urlparse(url).netloc.lower()
    return any (d in netloc for d in DOMAIN_ALLOW)

def is_file(url: str) -> bool:
    # Verifica se a URL termina com uma das extensões de arquivo especificadas.
    return url.lower().endswith(FILE_EXTENSIONS)

def is_pdf_interesting(url: str) -> bool:
    # Verifica se o nome do arquivo PDF contém alguma das palavras-chave especificadas.
    u = url.lower()
    return any(k in u for k in PDF_KEYWORDS)

def should_download(url: str) -> bool:
    # Determina se o arquivo na URL deve ser baixado.
    u = url.lower()
    if u.endswith(".zip"):
        return True
    if u.endswith((".csv", ".xls", ".xlsx", ".doc", ".docx")):
        return True
    if u.endswith(".pdf"):
        return is_pdf_interesting(u)
    return False

def infer_tipo(url: str) -> str:
    # Infere o tipo de documento com base na URL.
    return Path(urlparse(url).path).suffix.lower().replace('.', '')

# ============================
# Parte do donwload
# ============================

def download_file(session, url: str, out_dir: Path, referer: str):
    try:
        headers = {"Referer": referer}
        r = session.get(url, headers=headers, timeout=40)
        r.raise_for_status()
    except Exception as e:
        print(f"[403/BLOCK] {url}")
        return None

    file_hash = sha1_bytes(r.content)
    ext = Path(urlparse(url).path).suffix.lower()
    if not ext:
        return None

    filename = f"{file_hash}{ext}"
    dest = out_dir / filename

    if dest.exists():
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(r.content)

    return dest

# ============================
# Parte do crawler
# ============================

def crawl():
    session = requests.Session()
    session.headers.update(HEADERS)

    visited = set()
    failed_downloads = set()

    queue = SEEDS.copy()
    downloaded = []

    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            # w section
            r = session.get(url, timeout=20)
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue
        except Exception:
            continue

        soup = BeautifulSoup(r.text, "lxml")

        for a in soup.find_all("a", href=True):
            href = urljoin(url, a['href'].strip())

            if not is_internal(href):
                continue

            # download 
            if is_file(href) and should_download(href):

                if href in failed_downloads:
                    continue  # ❌ já falhou antes, não insiste

                tipo = infer_tipo(href)
                out_dir = OUT_BASE / tipo

                file_path = download_file(
                    session=session,
                    url=href,
                    out_dir=out_dir,
                    referer=url
                )

                if file_path:
                    meta = {
                        "file": file_path.name,
                        "url": href,
                        "tipo": tipo,
                        "source_page": url
                    }
                    downloaded.append(meta)
                    print(f"[OK] {href}")
                else:
                    failed_downloads.add(href)

            # ==========================
            # NAVEGAÇÃO (permissiva)
            # ==========================
            if href not in visited:
                queue.append(href)

        time.sleep(REQUEST_DELAY)

    return downloaded

# ============================
# Execução principal (vulgo main)
# ============================  

if __name__ == "_main_":
    results = crawl()

    meta_path = OUT_BASE / "index.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n Scrapping finalizado. {len(results)} arquivos baixados.")