import glob, os

for f in glob.glob(os.path.expanduser("~/.local/share/uv/tools/**/*.py"), recursive=True):
    if "manager.py" not in f or "/sdk/" not in f:
        continue

    lines = open(f).readlines()
    new_lines = []
    changed = False

    for line in lines:
        # Fix 1: wrap progressbar update in try/except
        if "bar.update(bar.currval + len(content))" in line and "try" not in line:
            indent = len(line) - len(line.lstrip())
            ind = " " * indent
            new_lines.append(ind + "try:\n")
            new_lines.append(ind + "    " + line.lstrip())
            new_lines.append(ind + "except (ValueError, Exception):\n")
            new_lines.append(ind + "    pass\n")
            changed = True
            continue

        # Fix 2: insert setuptools<58 before requirements.txt pip install
        if '"pip", "install", "-r",' in line and "setuptools" not in line and "check_call" in line:
            indent = len(line) - len(line.lstrip())
            ind = " " * indent
            start = line.index("subprocess.check_call([") + len("subprocess.check_call([")
            py_end = line.index('", "-m"')
            py_expr = line[start:py_end]
            new_lines.append(f'{ind}subprocess.check_call([{py_expr}, "-m", "pip", "install", "setuptools<58"])\n')
            changed = True

        new_lines.append(line)

    if changed:
        open(f, "w").writelines(new_lines)
        print("Patched:", f)
    else:
        print("No changes:", f)
