import sys

with open('frontend/project.html', 'r', encoding='utf-8') as f:
    text = f.read()

# We need to move the <script src="/project.js?v=23"></script> to the very end before </body>
script_tag = '<script src="/project.js?v=23"></script>'
if script_tag in text:
    text = text.replace(script_tag, '')
    text = text.replace('</body>', script_tag + '\n</body>')

with open('frontend/project.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("project.html script tag moved.")
