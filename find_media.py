import os

target_exts = {".gif", ".mp4", ".webm"}
matches = []

for root, dirs, files in os.walk(r"c:\Users\Admin\Documents\Agentic AI"):
    # Skip heavy dirs
    if "node_modules" in dirs:
        dirs.remove("node_modules")
    if ".git" in dirs:
        dirs.remove(".git")
    if "dist" in dirs:
        dirs.remove("dist")
    if "activepieces-backend" in dirs:
        dirs.remove("activepieces-backend")
        
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in target_exts:
            matches.append(os.path.join(root, file))

for m in matches:
    print(m)
