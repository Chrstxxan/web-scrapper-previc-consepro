'''
módulo onde a mágica do scrapper acontece: baixa os arquivos das urls visitadas. SEM DUPLICAR  
'''

import hashlib
from urllib.parse import urlparse
from pathlib import Path

def sha1_bytes(b: bytes) -> str:
    # Retorna o hash SHA1 dos bytes fornecidos.
    return hashlib.sha1(b).hexdigest()

def download(session, url: str, out_dir: Path, state, referer: str):
    r = session.get(url, headers={"Referer": referer}, timeout=40)
    r.raise_for_status()

    h = sha1_bytes(r.content)

    if h in state.hashes:
        return None  # Já baixado
    
    ext = Path(urlparse(url).path).suffix.lower()
    if not ext:
        return None  # Sem extensão válida
    
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{h}{ext}"

    dest.write_bytes(r.content)
    state.save_hash(h)

    return dest, h