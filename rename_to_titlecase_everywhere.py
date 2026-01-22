# rename_to_titlecase_everywhere.py
# Renombra SOLO lo que esté en la lista (Views + JS + Templates + carpeta Paginas)
# usando SIEMPRE git mv (con salto temporal para Windows/case-insensitive).
# También actualiza referencias en .py y .html (paths templates, imports Views, y JS en templates).

import os
import re
import uuid
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict

# ================== CONFIG ==================
SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}
SKIP_FILES = {"__init__.py"}  # normalmente NO se renombra
ENSURE_VIEWS_INIT = True

RENAME_DIRS = [
    ("modulo/templates/paginas", "modulo/templates/Paginas"),
]

RENAME_FILES = [
    # ---- Views ----
    ("modulo/Views/Cargos.py", "modulo/Views/Cargos.py"),
    ("modulo/Views/CentrosCostos.py", "modulo/Views/CentrosCostos.py"),
    ("modulo/Views/Consultores.py", "modulo/Views/Consultores.py"),
    ("modulo/Views/Contactos.py", "modulo/Views/Contactos.py"),
    ("modulo/Views/DetalleGastos.py", "modulo/Views/DetalleGastos.py"),
    ("modulo/Views/DetallesCertificacion.py", "modulo/Views/DetallesCertificacion.py"),
    ("modulo/Views/DetallesCostosIndirectos.py", "modulo/Views/DetallesCostosIndirectos.py"),
    ("modulo/Views/Empleado.py", "modulo/Views/Empleado.py"),
    ("modulo/Views/Gastos.py", "modulo/Views/Gastos.py"),
    ("modulo/Views/Ind.py", "modulo/Views/Ind.py"),
    ("modulo/Views/Ipc.py", "modulo/Views/Ipc.py"),
    ("modulo/Views/Linea.py", "modulo/Views/Linea.py"),
    ("modulo/Views/LineaClienteCentroCostos.py", "modulo/Views/LineaClienteCentroCostos.py"),
    ("modulo/Views/Modulo.py", "modulo/Views/Modulo.py"),
    ("modulo/Views/Moneda.py", "modulo/Views/Moneda.py"),
    ("modulo/Views/Perfil.py", "modulo/Views/Perfil.py"),
    ("modulo/Views/Referencia.py", "modulo/Views/Referencia.py"),
    ("modulo/Views/TiposContactos.py", "modulo/Views/TiposContactos.py"),
    ("modulo/Views/TotalCostos.py", "modulo/Views/TotalCostos.py"),
    ("modulo/Views/TotalGasto.py", "modulo/Views/TotalGasto.py"),

    # ---- JS ----
    ("modulo/static/JS/Auth.js", "modulo/static/JS/Auth.js"),
    ("modulo/static/JS/Cargos.js", "modulo/static/JS/Cargos.js"),
    ("modulo/static/JS/CentrosCostos.js", "modulo/static/JS/CentrosCostos.js"),
    ("modulo/static/JS/ClientesContratos.js", "modulo/static/JS/ClientesContratos.js"),
    ("modulo/static/JS/Consultores.js", "modulo/static/JS/Consultores.js"),
    ("modulo/static/JS/Contacto.js", "modulo/static/JS/Contacto.js"),
    ("modulo/static/JS/ContratosOtrosSi.js", "modulo/static/JS/ContratosOtrosSi.js"),
    ("modulo/static/JS/DetalleGastos.js", "modulo/static/JS/DetalleGastos.js"),
    ("modulo/static/JS/DetallesCertificacion.js", "modulo/static/JS/DetallesCertificacion.js"),
    ("modulo/static/JS/DetallesCostosIndirectos.js", "modulo/static/JS/DetallesCostosIndirectos.js"),
    ("modulo/static/JS/Empleado.js", "modulo/static/JS/Empleado.js"),
    ("modulo/static/JS/EmpleadosEstudios.js", "modulo/static/JS/EmpleadosEstudios.js"),
    ("modulo/static/JS/Gastos.js", "modulo/static/JS/Gastos.js"),
    ("modulo/static/JS/HistorialCargos.js", "modulo/static/JS/HistorialCargos.js"),
    ("modulo/static/JS/Ind.js", "modulo/static/JS/Ind.js"),
    ("modulo/static/JS/InformesHistorialCargos.js", "modulo/static/JS/InformesHistorialCargos.js"),
    ("modulo/static/JS/Ipc.js", "modulo/static/JS/Ipc.js"),
    ("modulo/static/JS/Linea.js", "modulo/static/JS/Linea.js"),
    ("modulo/static/JS/Modulo.js", "modulo/static/JS/Modulo.js"),
    ("modulo/static/JS/Moneda.js", "modulo/static/JS/Moneda.js"),
    ("modulo/static/JS/Perfil.js", "modulo/static/JS/Perfil.js"),
    ("modulo/static/JS/Referencia.js", "modulo/static/JS/Referencia.js"),
    ("modulo/static/JS/Sidebar.js", "modulo/static/JS/Sidebar.js"),
    ("modulo/static/JS/TotalCostos.js", "modulo/static/JS/TotalCostos.js"),
    ("modulo/static/JS/TotalGastos.js", "modulo/static/JS/TotalGastos.js"),

    # ---- Templates ----
    ("modulo/templates/Login/Login.html", "modulo/templates/Login/Login.html"),
    ("modulo/templates/Modulo/Crear.html", "modulo/templates/Modulo/Crear.html"),
    ("modulo/templates/Modulo/Editar.html", "modulo/templates/Modulo/Editar.html"),
    ("modulo/templates/Modulo/Forms.html", "modulo/templates/Modulo/Forms.html"),
    ("modulo/templates/Modulo/Index.html", "modulo/templates/Modulo/Index.html"),
    ("modulo/templates/Base.html", "modulo/templates/Base.html"),
    ("modulo/templates/Paginas/Nosotros.html", "modulo/templates/Paginas/Nosotros.html"),
]

# ================== HELPERS ==================
def is_skipped_path(p: Path) -> bool:
    return any(part in SKIP_DIRS for part in p.parts)

def find_repo_root_from_cwd() -> Path:
    """Busca .git hacia arriba desde el directorio actual."""
    cur = Path.cwd().resolve()
    for _ in range(30):
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    raise SystemExit("❌ No encontré .git hacia arriba desde el directorio actual. Abre la consola en el repo y reintenta.")

def run_git(git_exe: str, args: list[str], repo_root: Path, apply: bool, verbose: bool):
    """Ejecuta git con buen diagnóstico."""
    cmd = [git_exe] + args
    if not apply:
        print(f"[DRY] " + " ".join(cmd))
        return

    try:
        subprocess.run(
            cmd,
            cwd=os.fspath(repo_root),
            check=True,
            stdout=None if verbose else subprocess.DEVNULL,
            stderr=None if verbose else subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as e:
        raise SystemExit(f"❌ No pude ejecutar git ni entrar al cwd.\n- git_exe: {git_exe}\n- cwd: {repo_root}\n- error: {e}")
    except subprocess.CalledProcessError as e:
        msg = e.stderr or str(e)
        raise SystemExit(f"❌ Error ejecutando git:\n- cmd: {' '.join(cmd)}\n- cwd: {repo_root}\n- error: {msg}")

def safe_git_mv_with_temp(git_exe: str, src: Path, dst: Path, repo_root: Path, apply: bool, verbose: bool):
    """
    Caso normal: git mv src dst
    Caso Windows case-only: src -> tmp -> dst
    """
    if src == dst:
        return

    src_s = os.fspath(src)
    dst_s = os.fspath(dst)

    if src_s.lower() == dst_s.lower():
        tmp = src.with_name(f"__tmp__casefix__{uuid.uuid4().hex}__{src.name}")
        run_git(git_exe, ["mv", src_s, os.fspath(tmp)], repo_root, apply, verbose)
        run_git(git_exe, ["mv", os.fspath(tmp), dst_s], repo_root, apply, verbose)
    else:
        run_git(git_exe, ["mv", src_s, dst_s], repo_root, apply, verbose)

def apply_dir_map(p: Path, applied_dir_pairs):
    p_str = os.fspath(p)
    for old_dir, new_dir in sorted(applied_dir_pairs, key=lambda x: len(os.fspath(x[0])), reverse=True):
        old_s = os.fspath(old_dir)
        if p_str == old_s or p_str.startswith(old_s + os.sep):
            rel = Path(p_str).relative_to(old_dir)
            return new_dir / rel
    return p

def ensure_parent(dst: Path, apply: bool):
    if dst.parent.exists():
        return
    if not apply:
        print(f"[DRY] mkdir -p {dst.parent}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)

def detect_collisions(pairs):
    bucket = defaultdict(list)
    for src, dst in pairs:
        bucket[os.fspath(dst).lower()].append(os.fspath(src))
    return {k: v for k, v in bucket.items() if len(set(v)) > 1}

def update_text_file(path: Path, replacers, apply: bool):
    try:
        txt = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        txt = path.read_text(encoding="cp1252")

    newtxt = txt
    for old, new in replacers:
        newtxt = newtxt.replace(old, new)

    if newtxt != txt:
        if not apply:
            print(f"[DRY] update refs: {path}")
            return
        path.write_text(newtxt, encoding="utf-8")

def update_references(repo_root: Path, file_pairs_orig, dir_pairs_orig, apply: bool):
    templates_root = repo_root / "modulo" / "templates"
    js_root = repo_root / "modulo" / "static" / "JS"
    views_root = repo_root / "modulo" / "Views"
    this_script = Path(__file__).resolve()

    templates_path_map = {}

    for src, dst in dir_pairs_orig:
        try:
            if templates_root in src.parents or src == templates_root:
                old_rel = src.relative_to(templates_root).as_posix().rstrip("/") + "/"
                new_rel = dst.relative_to(templates_root).as_posix().rstrip("/") + "/"
                templates_path_map[old_rel] = new_rel
        except Exception:
            pass

    for src, dst in file_pairs_orig:
        try:
            if templates_root in src.parents:
                old_rel = src.relative_to(templates_root).as_posix()
                new_rel = dst.relative_to(templates_root).as_posix()
                templates_path_map[old_rel] = new_rel
        except Exception:
            pass

    templates_path_map = dict(sorted(templates_path_map.items(), key=lambda kv: len(kv[0]), reverse=True))
    tpl_pairs = list(templates_path_map.items())

    js_map = {}
    for src, dst in file_pairs_orig:
        try:
            if js_root in src.parents and src.suffix.lower() == ".js":
                js_map[src.stem] = dst.stem
        except Exception:
            pass
    static_pairs = [(f"JS/{old}.js", f"JS/{new}.js") for old, new in js_map.items()]

    views_mod_map = {}
    for src, dst in file_pairs_orig:
        try:
            if views_root in src.parents and src.suffix.lower() == ".py":
                if src.name not in SKIP_FILES:
                    views_mod_map[src.stem] = dst.stem
        except Exception:
            pass

    py_files = list(repo_root.rglob("*.py"))
    for p in py_files:
        if p.resolve() == this_script:
            continue

        try:
            txt = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            txt = p.read_text(encoding="cp1252")

        newtxt = txt

        for old, new in tpl_pairs:
            newtxt = newtxt.replace(old, new)

        for old_mod, new_mod in views_mod_map.items():
            if old_mod == new_mod:
                continue

            patterns = [
                (rf"(from\s+modulo\.Views\s+import\s+){old_mod}(\b)", rf"\1{new_mod}\2"),
                (rf"(from\s+modulo\.Views\.){old_mod}(\s+import\s+)", rf"\1{new_mod}\2"),
                (rf"(import\s+modulo\.Views\.){old_mod}(\b)", rf"\1{new_mod}\2"),
                (rf"(from\s+\.Views\s+import\s+){old_mod}(\b)", rf"\1{new_mod}\2"),
                (rf"(from\s+\.Views\.){old_mod}(\s+import\s+)", rf"\1{new_mod}\2"),
                (rf"(import\s+\.Views\.){old_mod}(\b)", rf"\1{new_mod}\2"),
            ]
            for pat, rep in patterns:
                newtxt = re.sub(pat, rep, newtxt)

        if newtxt != txt:
            if not apply:
                print(f"[DRY] update refs: {p}")
            else:
                p.write_text(newtxt, encoding="utf-8")

    html_files = list(templates_root.rglob("*.html")) if templates_root.exists() else []
    for h in html_files:
        update_text_file(h, tpl_pairs + static_pairs, apply)

def ensure_views_init(repo_root: Path, apply: bool):
    if not ENSURE_VIEWS_INIT:
        return
    views_init = repo_root / "modulo" / "Views" / "__init__.py"
    if views_init.exists():
        return
    if not apply:
        print(f"[DRY] create {views_init}")
        return
    views_init.write_text("# Views package\n", encoding="utf-8")

# ================== MAIN ==================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Ejecuta los cambios reales")
    parser.add_argument("--verbose", action="store_true", help="Muestra detalles")
    args = parser.parse_args()

    repo_root = find_repo_root_from_cwd()
    git_exe = "git" # O la ruta completa si es necesario
    
    print(f"Repo root: {repo_root}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")

    # 1. Renombrar Directorios
    print("\n================ RENOMBRANDO DIRECTORIOS ================")
    for old_s, new_s in RENAME_DIRS:
        src, dst = repo_root / old_s, repo_root / new_s
        if src.exists():
            print(f"📁 {old_s} -> {new_s}")
            safe_git_mv_with_temp(git_exe, src, dst, repo_root, args.apply, args.verbose)

    # 2. Renombrar Archivos
    print("\n================ RENOMBRANDO ARCHIVOS ================")
    replacements = []
    for old_s, new_s in RENAME_FILES:
        src, dst = repo_root / old_s, repo_root / new_s
        if src.exists():
            print(f"📄 {old_s} -> {new_s}")
            safe_git_mv_with_temp(git_exe, src, dst, repo_root, args.apply, args.verbose)
            # Guardamos para reemplazar en texto: "Cargos.py" -> "Cargos.py"
            replacements.append((Path(old_s).name, Path(new_s).name))
            # Guardamos para rutas de templates: "Paginas/Nosotros.html" -> "Paginas/Nosotros.html"
            clean_old = old_s.replace("modulo/templates/", "")
            clean_new = new_s.replace("modulo/templates/", "")
            replacements.append((clean_old, clean_new))

    # 3. Actualizar Referencias
    print("\n================ ACTUALIZANDO REFERENCIAS ================")
    if not args.apply:
        print("[DRY] Se saltó la actualización de texto.")
    else:
        # Buscamos en archivos .py, .html y .js
        for ext in ["**/*.py", "**/*.html", "**/*.js"]:
            for f_path in repo_root.glob(ext):
                if not is_skipped_path(f_path):
                    update_text_file(f_path, replacements, args.apply)

    print("\n✅ Listo.")

if __name__ == "__main__":
    main()