import glob, os, re

pattern = r'(\s+)(bar\.update\(bar\.currval \+ len\(content\)\))'
replacement = (r'\1try:\n'
               r'\1    bar.update(bar.currval + len(content))\n'
               r'\1except (ValueError, Exception):\n'
               r'\1    pass')

for f in glob.glob(os.path.expanduser("~/.local/share/uv/tools/**/*.py"), recursive=True):
    if "manager.py" in f and "/sdk/" in f:
        txt = open(f).read()
        new_txt = re.sub(pattern, replacement, txt)
        if new_txt != txt:
            open(f, "w").write(new_txt)
            print("Patched:", f)
        else:
            print("No match in:", f)
