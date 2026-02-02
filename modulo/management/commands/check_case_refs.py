#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path, PurePosixPath

TEMPLATE_ROOTS = [Path("modulo/templates")]
STATIC_ROOTS = [Path("modulo/static")]
CODE_ROOTS = [Path("modulo"), Path("sistema")]

# Python -> templates
RE_RENDER = re.compile(r'render\([^,]+,\s*["\'](?P<path>[^"\']+\.html)["\']')
RE_TEMPLATE_NAME = re.compile(r'template_name\s*=\s*["\'](?P<path>[^"\']+\.html)["\']')
RE_GET_TEMPLATE = re.compile(r'get_template\(\s*["\'](?P<path>[^"\']+\.html)["\']\s*\)')

# Templates -> templates/static
RE_EXTENDS_INCLUDE = re.compile(r'{%\s*(?:extends|include)\s+["\'](?P<path>[^"\']+\.html)["\']\s*%}')
RE_STATIC = re.compile(r'{%\s*static\s+["\'](?P<path>[^"\']+)["\']\s*%}')

def exists_case_sensitive(root: Path, rel_posix: str) -> bool:
    rel_posix = rel_posix.lstrip("/")
    parts = PurePosixPath(rel_posix).parts
    cur = root
    for part in parts:
        if not cur.exists() or not cur.is_dir():
            return False
        # listado real de nombres (case real)
        entries = {p.name: p for p in cur.iterdir()}
        if part not in entries:
            return False
        cur = entries[part]
    return cur.exists()

def build_lower_map(root: Path) -> dict[str, str]:
    m: dict[str, str] = {}
    if not root.exists():
        return m
    for p in root.rglob("*"):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            m.setdefault(rel.lower(), rel)  # si hay colisión, deja el primero
    return m

def find_refs_in_text(text: str, regex: re.Pattern) -> list[tuple[str, int]]:
    out = []
    for m in regex.finditer(text):
        path = m.group("path")
        line = text.count("\n", 0, m.start()) + 1
        out.append((path, line))
    return out

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return path.read_text(errors="replace")

def main() -> int:
    template_maps = [(root, build_lower_map(root)) for root in TEMPLATE_ROOTS]
    static_maps = [(root, build_lower_map(root)) for root in STATIC_ROOTS]

    problems: list[str] = []

    # 1) Buscar referencias a templates desde Python
    for root in CODE_ROOTS:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            txt = read_text(py)
            refs = []
            refs += find_refs_in_text(txt, RE_RENDER)
            refs += find_refs_in_text(txt, RE_TEMPLATE_NAME)
            refs += find_refs_in_text(txt, RE_GET_TEMPLATE)

            for rel, line in refs:
                ok_any = False
                suggestion = None
                for troot, lmap in template_maps:
                    if exists_case_sensitive(troot, rel):
                        ok_any = True
                        break
                    cand = lmap.get(rel.lower())
                    if cand:
                        suggestion = cand
                if not ok_any:
                    if suggestion:
                        problems.append(
                            f"[TEMPLATE CASE] {py.as_posix()}:{line} -> '{rel}'  (debería ser '{suggestion}')"
                        )
                    else:
                        problems.append(
                            f"[TEMPLATE MISSING] {py.as_posix()}:{line} -> '{rel}'  (no existe en templates escaneados)"
                        )

    # 2) Buscar extends/include/static dentro de templates
    for troot, lmap_templates in template_maps:
        if not troot.exists():
            continue
        for html in troot.rglob("*.html"):
            txt = read_text(html)

            # extends/include
            for rel, line in find_refs_in_text(txt, RE_EXTENDS_INCLUDE):
                if exists_case_sensitive(troot, rel):
                    continue
                cand = lmap_templates.get(rel.lower())
                if cand:
                    problems.append(
                        f"[INCLUDE/EXTENDS CASE] {html.as_posix()}:{line} -> '{rel}'  (debería ser '{cand}')"
                    )
                else:
                    problems.append(
                        f"[INCLUDE/EXTENDS MISSING] {html.as_posix()}:{line} -> '{rel}'  (no existe en {troot.as_posix()})"
                    )

            # static
            for rel, line in find_refs_in_text(txt, RE_STATIC):
                ok_any = False
                suggestion = None
                for sroot, lmap_static in static_maps:
                    if exists_case_sensitive(sroot, rel):
                        ok_any = True
                        break
                    cand = lmap_static.get(rel.lower())
                    if cand:
                        suggestion = cand
                if not ok_any:
                    if suggestion:
                        problems.append(
                            f"[STATIC CASE] {html.as_posix()}:{line} -> '{rel}'  (debería ser '{suggestion}')"
                        )
                    else:
                        problems.append(
                            f"[STATIC MISSING] {html.as_posix()}:{line} -> '{rel}'  (no existe en static escaneados)"
                        )

    if problems:
        print("\n".join(problems))
        print(f"\n❌ Encontré {len(problems)} problema(s) de rutas/case.")
        return 2

    print("✅ OK: No encontré problemas de case en render/extends/include/static.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
