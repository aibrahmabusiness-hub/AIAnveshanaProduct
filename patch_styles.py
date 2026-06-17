import re

file_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\style.css"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace all occurrences of `:not(#view-workflows):not(#view-runs)` with `:not(#view-workflows):not(#view-runs):not(#view-knowledge)`
new_content = content.replace(":not(#view-workflows):not(#view-runs)", ":not(#view-workflows):not(#view-runs):not(#view-knowledge)")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Patched style.css successfully.")
