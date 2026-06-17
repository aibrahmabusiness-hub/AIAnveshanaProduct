import sys
import os

file_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove sidebar nav item
nav_item_start = content.find('<div class="ws-nav-item" data-view="connections">')
if nav_item_start != -1:
    nav_item_end = content.find('</div>', nav_item_start) + 6 # Include closing div
    # Wait, the inner div has SVG and text, so there are no nested divs inside ws-nav-item.
    # We can just remove it.
    content = content[:nav_item_start] + content[nav_item_end:]

# 2. Remove the view-connections block
view_start = content.find('<!-- Connections View -->')
if view_start != -1:
    # Find the next view comment to safely cut
    view_end = content.find('<!-- Workflows View -->', view_start)
    if view_end != -1:
        content = content[:view_start] + content[view_end:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Removed Connections page from project.html.")
