import base64

sn_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12.02 0a11.98 11.98 0 1 0 0 23.96A11.98 11.98 0 0 0 12.02 0zm-3.66 17.5a1.85 1.85 0 0 1-1.85-1.85v-7.3a1.85 1.85 0 0 1 1.85-1.85h7.3a1.85 1.85 0 0 1 1.85 1.85v7.3a1.85 1.85 0 0 1-1.85 1.85h-7.3z" fill="#032D42"/></svg>'
sf_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M11.98 0C5.36 0 0 5.36 0 11.98c0 6.62 5.36 11.98 11.98 11.98s11.98-5.36 11.98-11.98S18.6 0 11.98 0zm4.5 17h-9c-2.48 0-4.5-2.02-4.5-4.5S5.02 8 7.5 8c.28 0 .54.04.8.1.72-1.8 2.5-3.1 4.7-3.1 2.22 0 4 1.3 4.7 3.1.26-.06.52-.1.8-.1 2.48 0 4.5 2.02 4.5 4.5s-2.02 4.5-4.5 4.5z" fill="#00A1E0"/></svg>'

sn_b64 = "data:image/svg+xml;base64," + base64.b64encode(sn_svg.encode('utf-8')).decode('utf-8')
sf_b64 = "data:image/svg+xml;base64," + base64.b64encode(sf_svg.encode('utf-8')).decode('utf-8')

with open('frontend/project.js', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("'https://cdn.worldvectorlogo.com/logos/servicenow-1.svg'", f"'{sn_b64}'")
text = text.replace("'https://cdn.worldvectorlogo.com/logos/salesforce-2.svg'", f"'{sf_b64}'")

with open('frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(text)

with open('frontend/project.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('v=28', 'v=29')
with open('frontend/project.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated successfully")
