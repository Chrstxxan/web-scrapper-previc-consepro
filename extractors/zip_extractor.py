import zipfile
import hashlib
from pathlib import Path

def sha1_bytes(b: bytes) -> str:
    # Retorna o hash SHA1 dos bytes fornecidos.
    return hashlib.sha1(b).hexdigest()

def extract_zip(zip_path: Path, out_base: Path, state):
    extracted = []

    with zipfile.ZipFile(zip_path, 'r') as z:
        for name in z.namelist():
            if name.endswith('/'):
                continue  # arquivo é um diretório

            content = z.read(name)
            h = sha1_bytes(content)

            if h in state.hashes:
                continue  # Já extraído

            ext = Path(name).suffix.lower().replace('.', '')
            out_dir = out_base / ext
            out_dir.mkdir(parents=True, exist_ok=True)

            dest = out_dir / f"{h}.{ext}"
            dest.write_bytes(content)

            state.save_hash(h)
            
            extracted.append({
                "file": dest.name,
                "hash": h,
                "tipo": ext,
                "origem": "zip",
                "container": zip_path.name
            })

    return extracted