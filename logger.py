import logging
from pathlib import Path

def setup_logger(log_dir: Path):
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "crawler.log"

    logger = logging.getLogger("PREVIC")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S"
    )

    # Terminal
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    # Arquivo
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(formatter)

    logger.addHandler(sh)
    logger.addHandler(fh)

    return logger