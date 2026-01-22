# sistema/env.py
from __future__ import annotations

import os
from pathlib import Path


def _parse_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        data[k] = v
    return data


def load_env() -> None:
    """
    Carga variables de entorno desde:
    1) ENV_FILE (ruta absoluta) si existe.
    2) fallback: .env en la raíz del repo (opcional).
    No sobreescribe variables ya existentes (usa setdefault).
    """
    # 1) si el sistema ya tiene vars (Render), eso manda.
    env_file = os.environ.get("ENV_FILE", "").strip()

    candidates: list[Path] = []
    if env_file:
        candidates.append(Path(env_file))

    # fallback opcional: .env en raíz del repo
    repo_root = Path(__file__).resolve().parents[1]  # .../<repo>/sistema/env.py -> <repo>/
    candidates.append(repo_root / ".env")

    for p in candidates:
        if p.exists() and p.is_file():
            parsed = _parse_env_file(p)
            for k, v in parsed.items():
                os.environ.setdefault(k, v)
            break
