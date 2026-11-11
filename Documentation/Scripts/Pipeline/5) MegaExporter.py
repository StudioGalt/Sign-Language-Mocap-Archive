import bpy
import os
import time
import traceback
from datetime import datetime

# ---------------------------------------------------------------------------
SCRIPTS = [
    # "AI Export.py",       # control passes for AI video (OpenPose / depth / lineart); not published
    "Normal Exporter.py",
    "Process Rigs.py",
    "Bundler.py"              
]

STOP_ON_ERROR = True

# Your workspace folder: edit this, or set the GALT_WORKSPACE environment variable before starting Blender.
WORKSPACE = os.environ.get("GALT_WORKSPACE", r"H:\Galt Workspace")

EXTRA_DIRS = [
    WORKSPACE,
    os.path.join(WORKSPACE, "Scripts"),
]

SEARCH_ROOT = WORKSPACE   # recursive fallback; None to disable

SKIP_DIR_NAMES = {"control_passes", "__pycache__", ".git",
                  "node_modules", "cache", "renders"}
# ---------------------------------------------------------------------------


def find_script(name):
    """Resolve a SCRIPTS entry to a real path, or None."""
    # full path given
    if os.path.isabs(name) or os.sep in name or "/" in name:
        return name if os.path.isfile(name) else None

    candidates = []

    def check(folder):
        p = os.path.join(folder, name)
        if os.path.isfile(p):
            candidates.append(p)

    blend_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None
    if blend_dir:
        d = blend_dir
        for _ in range(4):          # blend dir + 3 parents
            check(d)
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent

    for d in EXTRA_DIRS:
        if os.path.isdir(d):
            check(d)

    if candidates:
        return max(candidates, key=os.path.getmtime)

    if SEARCH_ROOT and os.path.isdir(SEARCH_ROOT):
        print(f"[launcher] {name!r} not in known folders, "
              f"walking {SEARCH_ROOT} ...")
        for root, dirs, files in os.walk(SEARCH_ROOT):
            dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIR_NAMES]
            if name in files:
                candidates.append(os.path.join(root, name))
        if candidates:
            return max(candidates, key=os.path.getmtime)

    return None


def execute(path):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    globs = {
        "__name__": "__main__",
        "__file__": path,
        "__builtins__": __builtins__,
    }
    exec(compile(source, path, "exec"), globs)


def run():
    # Resolve everything up front so a typo in script #2 is caught BEFORE
    # spending an hour rendering in script #1.
    resolved = []
    missing = []
    for name in SCRIPTS:
        path = find_script(name)
        (resolved if path else missing).append((name, path))
    if missing:
        raise RuntimeError(
            "Could not locate: "
            + ", ".join(repr(n) for n, _ in missing)
            + ". Use full paths in SCRIPTS or add their folder to EXTRA_DIRS.")

    print("[launcher] sequence:")
    for i, (name, path) in enumerate(resolved, 1):
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        print(f"  {i}. {path}  (modified {mtime:%Y-%m-%d %H:%M})")

    results = []
    for i, (name, path) in enumerate(resolved, 1):
        print("\n" + "=" * 70)
        print(f"[launcher] ({i}/{len(resolved)}) running {name}")
        print("=" * 70)
        t0 = time.time()
        try:
            execute(path)
            dt = time.time() - t0
            results.append((name, f"OK ({dt:.1f}s)"))
            print(f"[launcher] {name} finished in {dt:.1f}s")
        except Exception:
            dt = time.time() - t0
            results.append((name, f"FAILED ({dt:.1f}s)"))
            print(f"[launcher] {name} FAILED after {dt:.1f}s:")
            traceback.print_exc()
            if STOP_ON_ERROR:
                for later, _ in resolved[i:]:
                    results.append((later, "skipped"))
                break

    print("\n" + "=" * 70)
    print("[launcher] summary:")
    for name, status in results:
        print(f"  {status:>14}  {name}")
    print("=" * 70)


run()
