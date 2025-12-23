'''
coracao do sistema, aqui ele descobre os links e arquivos a partir das seeds, navega por todo o site.
'''

import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from config import DOMAIN_ALLOW, FILE_EXTENSIONS, REQUEST_DELAY, PATH_FOCUSED_ALLOW

def is_internal(url: str) -> bool:
    # Verifica se a URL pertence aos domínios permitidos.
    u = url.lower()
    return any(d in u for d in DOMAIN_ALLOW)

def is_file(url):
    # Verifica se a URL termina com uma das extensões de arquivo especificadas.
    return url.lower().endswith(FILE_EXTENSIONS)

def crawl(session, seeds, state, downloader, storage, out_base, logger, mode):
    queue = list(state.queue) if state.queue else list(seeds)
    logger.info(f"Iniciando o crawl com {len(queue)} URLs na fila.")

    while queue:
        url = queue.pop(0)
        logger.info(f"Visitando: {url}")
        state.save_queue(queue)
        if url in state.visited: 
            continue  # Já visitado

        state.save_visited(url)

        try:
            r = session.get(url, timeout=20)
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue  # Não é HTML

        except Exception:
            continue  # Erro ao acessar

        soup = BeautifulSoup(r.text, "lxml")

        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"].strip())
            parsed = urlparse(href)
            if mode == "focused":
                if not any(p in parsed.path for p in PATH_FOCUSED_ALLOW):
                    continue

            if parsed.fragment: 
                continue  # Ignora fragmentos

            if not is_internal(href):
                continue  # Fora do domínio

            if is_file(href):
                logger.info(f"Baixando arquivo: {href}")
                try:
                    result = downloader(
                        session=session,
                        url=href,
                        out_dir=out_base / parsed.path.split(".")[-1].lower(),
                        state=state,
                        referer=url
                    )
                    if result:
                        dest, h = result
                        logger.info(f"Arquivo salvo: {dest.name}")
                        storage(out_base, {
                            "file": dest.name,
                            "url": href,
                            "hash": h,
                            "tipo": dest.suffix.replace('.', ''),
                            "source_page": url
                        })

                        if dest.suffix.lower() == ".zip":
                            logger.info(f"Extraindo ZIP: {dest.name}")
                            from extractors.zip_extractor import extract_zip

                            extracted = extract_zip(dest, out_base, state)

                            for e in extracted:
                                storage(out_base, e)
                except Exception as e:
                    state.save_failed(href)
                    logger.error(f"Falha ao baixar: {href} | erro={e}")
            else:
                if href not in state.visited:
                    queue.append(href)
                    logger.debug(f"URL adicionada à fila: {href}")
                    state.save_queue(queue)
        time.sleep(REQUEST_DELAY)
    state.queue_path.unlink(missing_ok=True)
    logger.info("Fila finalizada e limpa.")