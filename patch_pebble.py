import glob, os

pat = "bar.update(bar.currval + len(content))"
fix = ("try:\n"
       "                bar.update(bar.currval + len(content))\n"
       "            except (ValueError, Exception):\n"
       "                pass")

for f in glob.glob(os.path.expanduser("~/.local/share/uv/tools/**/*.py"), recursive=True):
    if "manager.py" in f and "/sdk/" in f:
        txt = open(f).read()
        if pat in txt:
            open(f, "w").write(txt.replace(pat, fix))
            print("Patched:", f)
