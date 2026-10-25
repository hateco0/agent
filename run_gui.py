from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.logging_setup import log  # noqa: F401
    log.info("GUI старт")
except Exception:
    pass

from gui.app import App


if __name__ == "__main__":
    app = App()
    app.mainloop()
