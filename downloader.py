'''
módulo onde a mágica do scrapper acontece: baixa os arquivos das urls visitadas. SEM DUPLICAR  
'''

import hashlib
import re
from urllib.parse import urlparse, unquote
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
    
    # 🔹 nome original do arquivo a partir da URL
    parsed = urlparse(url)
    orig_name = Path(unquote(parsed.path)).name

    if not orig_name:
        orig_name = "arquivo"

    # 🔹 sanitiza o nome (seguro para Windows/Linux)
    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", orig_name).lower()

    ext = Path(safe_name).suffix.lower()
    if not ext:
        return None  # Sem extensão válida

    out_dir.mkdir(parents=True, exist_ok=True)

    # 🔹 NOME HÍBRIDO: hash + nome humano
    filename = f"{h}__{safe_name}"
    dest = out_dir / filename

    dest.write_bytes(r.content)
    state.save_hash(h)

    return dest, h