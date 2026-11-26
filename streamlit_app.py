import os
import sys
import runpy

# Ensure src is in sys.path
src_dir = os.path.join(os.path.dirname(__file__), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Run src/app.py
app_path = os.path.join(src_dir, "app.py")
runpy.run_path(app_path, run_name="__main__")
