"""Entrada do backend na Vercel: a função Python que atende todas as rotas /api.

O código fica em backend/app; aqui só o tornamos importável e expomos o app FastAPI.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402, F401
