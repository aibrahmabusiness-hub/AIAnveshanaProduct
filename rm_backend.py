import shutil
import os

path = r"c:\Users\Admin\Documents\Agentic AI\activepieces-backend"
if os.path.exists(path):
    # Fix for windows long paths
    path = "\\\\?\\" + path
    shutil.rmtree(path, ignore_errors=True)
