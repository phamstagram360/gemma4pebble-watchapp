import glob, os, re

def patch_file(f, old, new):
    txt = open(f).read()
    if old in txt:
        open(f, "w").write(txt.replace(old, new))
        print("Patched:", f, "->", repr(old[:40]))
        return True
    print("No match:", repr(old[:40]), "in", f)
    return False

for f in glob.glob(os.path.expanduser("~/.local/share/uv/tools/**/*.py"), recursive=True):
    if "manager.py" not in f or "/sdk/" not in f:
        continue

    # Fix 1: progressbar ValueError
    patch_file(f,
        "bar.update(bar.currval + len(content))",
        "try:\n                bar.update(bar.currval + len(content))\n            except (ValueError, Exception):\n                pass")

    # Fix 2: insert setuptools<58 install before requirements.txt install
    patch_file(f,
        'subprocess.check_call([os.path.join(venv_path, "bin", "python"), "-m", "pip", "install", "-r",',
        'subprocess.check_call([os.path.join(venv_path, "bin", "python"), "-m", "pip", "install", "setuptools<58"])\n        subprocess.check_call([os.path.join(venv_path, "bin", "python"), "-m", "pip", "install", "-r",')
