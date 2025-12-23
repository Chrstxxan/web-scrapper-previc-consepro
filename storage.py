'''
verificar se o arquivo ja foi baixado em alguma execução anterior
'''

import json
from datetime import datetime

def append_index(base, meta: dict):
    meta["timestamp"] = datetime.utcnow().isoformat()
    path = base / "index.json"

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(meta, ensure_ascii=False) + "\n")