'''
esse módulo serve como um arquivo que vai garantir que nenhum arquivo seja baixado mais de uma vez, guardando hashes dos arquivos já baixados, alem de nao permitir que o bot visite a mesma url mais de uma vez, basicamente nao permitindo insistir em erros.
obs: vou usar modelo de POO, para organizacao
'''

from importlib.resources import path
from pathlib import Path

class State:
    def __init__(self, base: Path):
        self.visited_path = base / "visited.txt"
        self.hashes_path = base / "hashes.txt"
        self.failed_path = base / "failed.txt"
        self.queue_path = base / "queue.txt"

        self.visited = self.load(self.visited_path)
        self.hashes = self.load(self.hashes_path)
        self.failed = self.load(self.failed_path)
        self.queue = self.load(self.queue_path)

    def load(self, path: Path) -> set:
        if not path.exists():
            return set()
        return set(path.read_text(encoding="utf-8").splitlines())
    
    def save_visited(self, url: str):
        self.visited.add(url)
        self.visited_path.write_text("\n".join(self.visited), encoding="utf-8")

    def save_hash(self, h: str):
        self.hashes.add(h)
        self.hashes_path.write_text("\n".join(self.hashes), encoding="utf-8")

    def save_failed(self, url: str):
        self.failed.add(url)
        self.failed_path.write_text("\n".join(self.failed), encoding="utf-8")

    def save_queue(self, queue: list):
        self.queue = list(queue)
        self.queue_path.write_text("\n".join(self.queue), encoding="utf-8")