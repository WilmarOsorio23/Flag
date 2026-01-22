#!/usr/bin/env python
import os
import sys
from pathlib import Path


def load_dotenv_file(dotenv_path: Path) -> None:
    if not dotenv_path or not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def main():
    # Cargar SOLO desde ENV_FILE (afuera del repo)
    env_file = os.environ.get("ENV_FILE")
    if env_file:
        load_dotenv_file(Path(env_file))

    # Resolver settings module (por env o fallback)
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        os.environ.get("DJANGO_SETTINGS_MODULE", "sistema.settings.development"),
    )

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
