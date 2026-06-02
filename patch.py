import os

files = ['index.html', 'login.html', 'signup.html']

for f in files:
    path = os.path.join('frontend', f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace('<head>', '<head>\n    <script src="config.js"></script>')
    content = content.replace('/static/', '')
    content = content.replace("fetch('/api", "fetch(API_BASE_URL + '/api")
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

print("Patched successfully")
