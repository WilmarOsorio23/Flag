# rename_to_titlecase_everywhere.py
# Renombra SOLO lo que esté en la lista (Views + JS + Templates + carpeta Paginas)
# usando SIEMPRE git mv y (para Windows/case-only) hace salto temporal.
# También actualiza referencias en .py y .html.

import os
import re
import uuid
import shutil
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict

# ================== CONFIG ==================
SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}
SKIP_FILES = {"__init__.py"}
ENSURE_VIEWS_INIT = True

RENAME_DIRS = [
    ("modulo/templates/paginas", "modulo/templates/Paginas"),
]

RENAME_FILES = [
    # ---- Views ----
    ("modulo/Views/cargos.py", "modulo/Views/Cargos.py"),
    ("modulo/Views/centrosCostos.py", "modulo/Views/CentrosCostos.py"),
    ("modulo/Views/consultores.py", "modulo/Views/Consultores.py"),
    ("modulo/Views/contactos.py", "modulo/Views/Contactos.py"),
    ("modulo/Views/detalleGastos.py", "modulo/Views/DetalleGastos.py"),
    ("modulo/Views/detallesCertificacion.py", "modulo/Views/DetallesCertificacion.py"),
    ("modulo/Views/detallesCostosIndirectos.py", "modulo/Views/DetallesCostosIndirectos.py"),
    ("modulo/Views/empleado.py", "modulo/Views/Empleado.py"),
    ("modulo/Views/gastos.py", "modulo/Views/Gastos.py"),
    ("modulo/Views/ind.py", "modulo/Views/Ind.py"),
    ("modulo/Views/ipc.py", "modulo/Views/Ipc.py"),
    ("modulo/Views/linea.py", "modulo/Views/Linea.py"),
    ("modulo/Views/lineaClienteCentroCostos.py", "modulo/Views/LineaClienteCentroCostos.py"),
    ("modulo/Views/modulo.py", "modulo/Views/Modulo.py"),
    ("modulo/Views/moneda.py", "modulo/Views/Moneda.py"),
    ("modulo/Views/perfil.py", "modulo/Views/Perfil.py"),
    ("modulo/Views/referencia.py", "modulo/Views/Referencia.py"),
    ("modulo/Views/tiposContactos.py", "modulo/Views/TiposContactos.py"),
    ("modulo/Views/totalCostos.py", "modulo/Views/TotalCostos.py"),
    ("modulo/Views/totalGasto.py", "modulo/Views/TotalGasto.py"),

    # ---- JS ----
    ("modulo/static/JS/auth.js", "modulo/static/JS/Auth.js"),
    ("modulo/static/JS/cargos.js", "modulo/static/JS/Cargos.js"),
    ("modulo/static/JS/centroscostos.js", "modulo/static/JS/CentrosCostos.js"),
    ("modulo/static/JS/clientesContratos.js", "modulo/static/JS/ClientesContratos.js"),
    ("modulo/static/JS/consultores.js", "modulo/static/JS/Consultores.js"),
    ("modulo/static/JS/contacto.js", "modulo/static/JS/Contacto.js"),
    ("modulo/static/JS/contratosOtrosSi.js", "modulo/static/JS/ContratosOtrosSi.js"),
    ("modulo/static/JS/detalleGastos.js", "modulo/static/JS/DetalleGastos.js"),
    ("modulo/static/JS/detallesCertificacion.js", "modulo/static/JS/DetallesCertificacion.js"),
    ("modulo/static/JS/detallesCostosIndirectos.js", "modulo/static/JS/DetallesCostosIndirectos.js"),
    ("modulo/static/JS/empleado.js", "modulo/static/JS/Empleado.js"),
    ("modulo/static/JS/empleadosEstudios.js", "modulo/static/JS/EmpleadosEstudios.js"),
    ("modulo/static/JS/gastos.js", "modulo/static/JS/Gastos.js"),
    ("modulo/static/JS/historialCargos.js", "modulo/static/JS/HistorialCargos.js"),
    ("modulo/static/JS/ind.js", "modulo/static/JS/Ind.js"),
    ("modulo/static/JS/informesHistorialCargos.js", "modulo/static/JS/InformesHistorialCargos.js"),
    ("modulo/static/JS/ipc.js", "modulo/static/JS/Ipc.js"),
    ("modulo/static/JS/linea.js", "modulo/static/JS/Linea.js"),
    ("modulo/static/JS/modulo.js", "modulo/static/JS/Modulo.js"),
    ("modulo/static/JS/moneda.js", "modulo/static/JS/Moneda.js"),
    ("modulo/static/JS/perfil.js", "modulo/static/JS/Perfil.js"),
    ("modulo/static/JS/referencia.js", "modulo/static/JS/Referencia.js"),
    ("modulo/static/JS/sidebar.js", "modulo/static/JS/Sidebar.js"),
    ("modulo/static/JS/totalCostos.js", "modulo/static/JS/TotalCostos.js"),
    ("modulo/static/JS/totalGastos.js", "modulo/static/JS/TotalGastos.js"),

    # ---- Templates ----
    ("modulo/templates/Login/login.html", "modulo/templates/Login/Login.html"),
    ("modulo/templates/Modulo/crear.html", "modulo/templates/Modulo/Crear.html"),
    ("modulo/templates/Modulo/editar.html", "modulo/templates/Modulo/Editar.html"),
    ("modulo/templates/Modulo/forms.html", "modulo/templates/Modulo/Forms.html"),
    ("modulo/templates/Modulo/index.html", "modulo/templates/Modulo/Index.html"),
    ("modulo/templates/base.html", "modulo/templates/Base.html"),
    ("modulo/templates/paginas/nosotros.html", "modulo/templates/Paginas/Nosotros.html"),
]

# ================== HELPERS ==================
def is_skipped_path(p: Path) -> bool:
    return any(part in SKIP_DIRS for part in p.parts)

def find_repo_root_from_cwd() -> Path:
    cur = Path.cwd().resolve()
    for _ in range(30):
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    raise SystemExit("❌ No encontré .git hacia arriba desde el directorio actual.")

def same_path_exact(src: Path, dst: Path) -> bool:
    # Comparación exacta (case-sensitive) del string del path.
    return os.fspath(src) == os.fspath(dst)

def is_case_only(src: Path, dst: Path) -> bool:
    # Mismo path ignorando mayúsculas (Windows case-insensitive)
    return os.fspath(src).lower() == os.fspath(dst).lower()

def run_git(git_exe: str, args: list[str], repo_root: Path, verbose: bool):
    cmd = [git_exe] + args
    subprocess.run(
        cmd,
        cwd=os.fspath(repo_root),
        check=True,
        stdout=None if verbose else subprocess.DEVNULL,
        stderr=None if verbose else subprocess.PIPE,
        text=True,
    )

def git_mv_safe(git_exe: str, src: Path, dst: Path, repo_root: Path, verbose: bool, dry: bool):
    # ❗️OJO: NO uses (src == dst) en Windows, porque ignora case.
    if same_path_exact(src, dst):
        print(f"[SKIP] (exact) {src}")
        return False

    if dry:
        if is_case_only(src, dst):
            tmp = src.with_name(f"__tmp__casefix__{uuid.uuid4().hex}__{src.name}")
            print(f"[DRY] git mv {src} -> {tmp}")
            print(f"[DRY] git mv {tmp} -> {dst}")
        else:
            print(f"[DRY] git mv {src} -> {dst}")
        return True

    if is_case_only(src, dst):
        tmp = src.with_name(f"__tmp__casefix__{uuid.uuid4().hex}__{src.name}")
        run_git(git_exe, ["mv", os.fspath(src), os.fspath(tmp)], repo_root, verbose)
        run_git(git_exe, ["mv", os.fspath(tmp), os.fspath(dst)], repo_root, verbose)
        print(f"[OK]  {src.relative_to(repo_root)} -> {dst.relative_to(repo_root)}  (case-only via tmp)")
        return True

    run_git(git_exe, ["mv", os.fspath(src), os.fspath(dst)], repo_root, verbose)
    print(f"[OK]  {src.relative_to(repo_root)} -> {dst.relative_to(repo_root)}")
    return True

def ensure_parent(dst: Path, dry: bool):
    if dst.parent.exists():
        return
    if dry:
        print(f"[DRY] mkdir -p {dst.parent}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)

def detect_collisions(pairs):
    bucket = defaultdict(list)
    for src, dst in pairs:
        bucket[os.fspath(dst).lower()].append(os.fspath(src))
    return {k: v for k, v in bucket.items() if len(set(v)) > 1}

def apply_dir_map(p: Path, applied_dir_pairs):
    p_str = os.fspath(p)
    for old_dir, new_dir in sorted(applied_dir_pairs, key=lambda x: len(os.fspath(x[0])), reverse=True):
        old_s = os.fspath(old_dir)
        if p_str == old_s or p_str.startswith(old_s + os.sep):
            rel = Path(p_str).relative_to(old_dir)
            return new_dir / rel
    return p

def update_text_file(path: Path, replacers, dry: bool) -> bool:
    try:
        txt = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        txt = path.read_text(encoding="cp1252")

    newtxt = txt
    for old, new in replacers:
        newtxt = newtxt.replace(old, new)

    if newtxt != txt:
        if dry:
            print(f"[DRY] update refs: {path}")
            return True
        path.write_text(newtxt, encoding="utf-8")
        return True
    return False

def update_references(repo_root: Path, file_pairs_orig, dir_pairs_orig, dry: bool):
    """
    Actualiza referencias en:
      - .py: template_name/render("...") e imports de Views.
      - .html: extends/include + static JS/CSS.
    """
    templates_root = repo_root / "modulo" / "templates"
    js_root = repo_root / "modulo" / "static" / "JS"
    views_root = repo_root / "modulo" / "Views"
    this_script = Path(__file__).resolve()

    # ---------- construir mapa de rutas de templates (relativas a modulo/templates) ----------
    tpl_map = {}

    # dirs (ej: paginas/ -> Paginas/)
    for src, dst in dir_pairs_orig:
        try:
            if templates_root in src.parents or src == templates_root:
                old_rel = src.relative_to(templates_root).as_posix().rstrip("/") + "/"
                new_rel = dst.relative_to(templates_root).as_posix().rstrip("/") + "/"
                tpl_map[old_rel] = new_rel
        except Exception:
            pass

    # files (ej: base.html -> Base.html, paginas/nosotros.html -> Paginas/Nosotros.html)
    for src, dst in file_pairs_orig:
        try:
            if templates_root in src.parents:
                old_rel = src.relative_to(templates_root).as_posix()
                new_rel = dst.relative_to(templates_root).as_posix()
                tpl_map[old_rel] = new_rel
        except Exception:
            pass

    # IMPORTANT: también detecta archivos movidos SOLO por el rename de carpeta (ej Inicio.html)
    # recorriendo git status no podemos aquí, pero sí podemos inferir por existencia real:
    # si "Paginas" ya existe, migrar cualquier "paginas/*.html" antiguo a "Paginas/*.html"
    old_paginas = templates_root / "paginas"
    new_paginas = templates_root / "Paginas"
    if new_paginas.exists():
        # Agrega un fallback genérico: "paginas/" -> "Paginas/"
        tpl_map["paginas/"] = "Paginas/"

    # ordenar por longitud desc para reemplazar primero lo más específico
    tpl_pairs = sorted(tpl_map.items(), key=lambda kv: len(kv[0]), reverse=True)

    # ---------- JS map ----------
    js_map = {}
    for src, dst in file_pairs_orig:
        try:
            if js_root in src.parents and src.suffix.lower() == ".js":
                js_map[src.name] = dst.name  # nombre completo con .js
        except Exception:
            pass

    # reemplazos para static
    static_pairs = []
    for old_name, new_name in js_map.items():
        static_pairs.append((f"JS/{old_name}", f"JS/{new_name}"))
        static_pairs.append((f"JS\\{old_name}", f"JS\\{new_name}"))  # por si alguien lo escribió mal con backslash

    # ---------- Views map (imports python) ----------
    views_mod_map = {}
    for src, dst in file_pairs_orig:
        try:
            if views_root in src.parents and src.suffix.lower() == ".py":
                if src.name not in SKIP_FILES:
                    views_mod_map[src.stem] = dst.stem
        except Exception:
            pass

    changed = 0

    def read_text_any(p: Path) -> str:
        try:
            return p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return p.read_text(encoding="cp1252")

    def write_text_utf8(p: Path, s: str):
        p.write_text(s, encoding="utf-8")

    # ----------------- actualizar .py -----------------
    for p in repo_root.rglob("*.py"):
        if p.resolve() == this_script:
            continue
        txt = read_text_any(p)
        newtxt = txt

        # template paths (ej "base.html", "paginas/nosotros.html")
        for old, new in tpl_pairs:
            newtxt = newtxt.replace(old, new)

        # también por si están usando solo el nombre (ej "base.html" sin folder)
        for old, new in tpl_pairs:
            if "/" in old:
                old_tail = old.split("/")[-1]
                new_tail = new.split("/")[-1]
                newtxt = newtxt.replace(old_tail, new_tail)

        # imports de Views
        for old_mod, new_mod in views_mod_map.items():
            if old_mod == new_mod:
                continue
            newtxt = re.sub(rf"(from\s+modulo\.Views\s+import\s+){old_mod}(\b)", rf"\1{new_mod}\2", newtxt)
            newtxt = re.sub(rf"(from\s+modulo\.Views\.){old_mod}(\s+import\s+)", rf"\1{new_mod}\2", newtxt)
            newtxt = re.sub(rf"(import\s+modulo\.Views\.){old_mod}(\b)", rf"\1{new_mod}\2", newtxt)

        if newtxt != txt:
            if dry:
                print(f"[DRY] update refs: {p}")
            else:
                write_text_utf8(p, newtxt)
            changed += 1

    # ----------------- actualizar .html -----------------
    if templates_root.exists():
        for h in templates_root.rglob("*.html"):
            txt = read_text_any(h)
            newtxt = txt

            # rutas completas (ej paginas/nosotros.html -> Paginas/Nosotros.html)
            for old, new in tpl_pairs:
                newtxt = newtxt.replace(old, new)

            # tails (ej base.html -> Base.html) para extends "base.html"
            for old, new in tpl_pairs:
                if "/" in old:
                    old_tail = old.split("/")[-1]
                    new_tail = new.split("/")[-1]
                    newtxt = newtxt.replace(old_tail, new_tail)

            # static JS (auth.js -> Auth.js)
            for old, new in static_pairs:
                newtxt = newtxt.replace(old, new)

            if newtxt != txt:
                if dry:
                    print(f"[DRY] update refs: {h}")
                else:
                    write_text_utf8(h, newtxt)
                changed += 1

    print(f"Refs actualizadas en {changed} archivo(s).")

def ensure_views_init(repo_root: Path, dry: bool):
    if not ENSURE_VIEWS_INIT:
        return
    views_init = repo_root / "modulo" / "Views" / "__init__.py"
    if views_init.exists():
        return
    if dry:
        print(f"[DRY] create {views_init}")
        return
    views_init.write_text("# Views package\n", encoding="utf-8")
    print(f"[OK]  created {views_init.relative_to(repo_root)}")

def print_git_status(git_exe: str, repo_root: Path):
    res = subprocess.run(
        [git_exe, "status", "--porcelain"],
        cwd=os.fspath(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out = (res.stdout or "").strip()
    print("\n" + "=" * 90)
    print("GIT STATUS (porcelain)")
    print("=" * 90)
    print(out if out else "✅ No hay cambios detectados por git (status limpio).")

# ================== MAIN ==================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--no-update-refs", action="store_true")
    parser.add_argument("--git-exe", default=os.environ.get("GIT_EXE"))
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    dry = not args.apply
    update_refs = not args.no_update_refs
    verbose = args.verbose

    repo_root = find_repo_root_from_cwd()
    git_exe = args.git_exe or shutil.which("git") or shutil.which("git.exe") or "git"

    print(f"Repo root: {repo_root}")
    print(f"Mode: {'APPLY' if not dry else 'DRY RUN'}")
    print(f"Use git: YES -> {git_exe}")
    print(f"Update references: {('YES' if update_refs else 'NO')}")

    # validar git
    subprocess.run([git_exe, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    subprocess.run([git_exe, "rev-parse", "--is-inside-work-tree"], cwd=os.fspath(repo_root),
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    dir_pairs_orig = [(repo_root / Path(a), repo_root / Path(b)) for a, b in RENAME_DIRS]
    file_pairs_orig = [(repo_root / Path(a), repo_root / Path(b)) for a, b in RENAME_FILES]

    dir_pairs_orig = [(s, d) for s, d in dir_pairs_orig if not is_skipped_path(s)]
    file_pairs_orig = [(s, d) for s, d in file_pairs_orig if not is_skipped_path(s)]

    collisions = detect_collisions(dir_pairs_orig + file_pairs_orig)
    if collisions:
        print("\n💥 COLISIONES detectadas (mismo destino final case-insensitive):")
        for dst_lc, sources in collisions.items():
            print(f"  -> {dst_lc}")
            for s in sources:
                print(f"     - {s}")
        raise SystemExit("Resuelve colisiones antes de aplicar renombres.")

    print("\n" + "=" * 90)
    print("MAPEO (lo que se renombraría)")
    print("=" * 90)
    print(f"\n📁 Directorios: {len(dir_pairs_orig)}")
    for src, dst in dir_pairs_orig:
        print(f"  {src.relative_to(repo_root)}  ->  {dst.relative_to(repo_root)}")
    print(f"\n📄 Archivos: {len(file_pairs_orig)}")
    for src, dst in file_pairs_orig:
        print(f"  {src.relative_to(repo_root)}  ->  {dst.relative_to(repo_root)}")

    print("\n" + "=" * 90)
    print("RENOMBRANDO" if not dry else "SIMULANDO RENOMBRADO")
    print("=" * 90)

    applied_dir_pairs = []

    # 1) directorios primero
    for src, dst in sorted(dir_pairs_orig, key=lambda p: len(os.fspath(p[0]).split(os.sep)), reverse=True):
        src_cur = apply_dir_map(src, applied_dir_pairs)
        dst_cur = apply_dir_map(dst, applied_dir_pairs)

        if not dry and not src_cur.exists():
            print(f"[WARN] dir no existe, skip: {src_cur.relative_to(repo_root)}")
            continue

        if not dry and (not is_case_only(src_cur, dst_cur)) and dst_cur.exists():
            print(f"[WARN] destino ya existe, skip: {dst_cur.relative_to(repo_root)}")
            continue

        moved = git_mv_safe(git_exe, src_cur, dst_cur, repo_root, verbose, dry)
        if moved and not dry:
            applied_dir_pairs.append((src_cur, dst_cur))

    # 2) archivos
    for src, dst in file_pairs_orig:
        src_cur = apply_dir_map(src, applied_dir_pairs)
        dst_cur = apply_dir_map(dst, applied_dir_pairs)

        if not dry and not src_cur.exists():
            print(f"[WARN] file no existe, skip: {src_cur.relative_to(repo_root)}")
            continue

        ensure_parent(dst_cur, dry)

        if not dry and (not is_case_only(src_cur, dst_cur)) and dst_cur.exists():
            print(f"[WARN] destino ya existe, skip: {dst_cur.relative_to(repo_root)}")
            continue

        git_mv_safe(git_exe, src_cur, dst_cur, repo_root, verbose, dry)

    ensure_views_init(repo_root, dry)

    if update_refs:
        print("\n" + "=" * 90)
        print("ACTUALIZANDO REFERENCIAS" if not dry else "SIMULANDO ACTUALIZACIÓN DE REFERENCIAS")
        print("=" * 90)
        update_references(repo_root, file_pairs_orig, dir_pairs_orig, dry)

    print_git_status(git_exe, repo_root)

    print("\n✅ Listo.")
    print("Siguiente:")
    print("  1) git status")
    print("  2) python manage.py check")
    print("  3) corre el server local")
    print("  4) commit + push")

if __name__ == "__main__":
    main()
