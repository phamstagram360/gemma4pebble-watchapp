import glob, os

for f in glob.glob(os.path.expanduser("~/.local/share/uv/tools/**/*.py"), recursive=True):
    if "manager.py" not in f or "/sdk/" not in f:
        continue

    txt = open(f).read()
    
    # Fix 1: Progress bar bug
    old1 = "bar.update(bar.currval + len(content))"
    new1 = "try: bar.update(bar.currval + len(content))\n            except: pass"
    
    # Fix 2: setuptools bug (pypng)
    old2 = 'subprocess.check_call([os.path.join(venv_path, "bin", "python"), "-m", "pip", "install", "-r",'
    new2 = 'subprocess.check_call([os.path.join(venv_path, "bin", "python"), "-m", "pip", "install", "setuptools<58"])\n        subprocess.check_call([os.path.join(venv_path, "bin", "python"), "-m", "pip", "install", "-r",'

    if old1 in txt or old2 in txt:
        txt = txt.replace(old1, new1).replace(old2, new2)
        open(f, "w").write(txt)
        print("Patched:", f)
