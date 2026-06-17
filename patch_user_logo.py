import base64

sn_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12.02 0a11.98 11.98 0 1 0 0 23.96A11.98 11.98 0 0 0 12.02 0zm-3.66 17.5a1.85 1.85 0 0 1-1.85-1.85v-7.3a1.85 1.85 0 0 1 1.85-1.85h7.3a1.85 1.85 0 0 1 1.85 1.85v7.3a1.85 1.85 0 0 1-1.85 1.85h-7.3z" fill="#032D42"/></svg>'
sn_b64 = "data:image/svg+xml;base64," + base64.b64encode(sn_svg.encode('utf-8')).decode('utf-8')

new_url = "https://upload.wikimedia.org/wikipedia/commons/5/57/ServiceNow_logo.svg"

with open('frontend/project.js', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(f"'{sn_b64}'", f"'{new_url}'")

with open('frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(text)

with open('frontend/project.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('v=29', 'v=30')
with open('frontend/project.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Replaced ServiceNow logo and bumped cache.")
