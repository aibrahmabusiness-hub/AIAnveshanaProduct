import re

with open('frontend/project.js', 'r', encoding='utf-8') as f:
    text = f.read()

targets = ['saveSfCreds', 'testSfCredsBtn', 'saveSnCreds', 'testSnCredsBtn', 'saveGmCreds', 'testGmCredsBtn', 'saveJrCreds', 'testJrCredsBtn']

for target in targets:
    # Use exact match to replace .addEventListener with ?.addEventListener
    find_str = f"document.getElementById('{target}').addEventListener"
    repl_str = f"document.getElementById('{target}')?.addEventListener"
    text = text.replace(find_str, repl_str)

with open('frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('Patched project.js successfully')
