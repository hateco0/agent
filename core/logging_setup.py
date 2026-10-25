from __future__ import annotations

import logging
from pathlib import Path

LOG_DIR = Path("data")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "agent_debug.log"

_logger = None


def setup_logging() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger
    logger = logging.getLogger("voice_os_agent")
    if logger.handlers:
        _logger = logger
        return _logger
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s", datefmt="%H:%M:%S")
    try:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    except Exception:
        pass
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)
    logger.propagate = False
    _logger = logger
    return _logger


log = setup_logging()
