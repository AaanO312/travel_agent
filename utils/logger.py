import logging
import os
from datetime import datetime

LOG_ROOT = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_ROOT, exist_ok=True)


def get_logger(name: str = "travel_agent") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        return logger
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(); ch.setLevel(logging.INFO); ch.setFormatter(fmt)
    fh = logging.FileHandler(os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log"), encoding="utf-8")
    fh.setLevel(logging.DEBUG); fh.setFormatter(fmt)
    logger.addHandler(ch); logger.addHandler(fh)
    return logger


logger = get_logger()
