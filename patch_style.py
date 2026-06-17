import sys

file_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\style.css"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_selector = ":not(#view-chat):not(#view-workflows):not(#view-runs):not(#view-knowledge).active"
new_selector = ":not(#view-chat):not(#view-workflows):not(#view-runs):not(#view-knowledge):not(#view-tools).active"

if old_selector in content:
    content = content.replace(old_selector, new_selector)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched style.css successfully")
else:
    print("Failed to find selector in style.css")
