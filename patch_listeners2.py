import re

with open('frontend/project.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace document.getElementById('...').addEventListener
# We don't want to replace ones that already have ?.
text = re.sub(r"(document\.getElementById\(['\"][a-zA-Z0-9_-]+['\"]\))\.addEventListener", r"\1?.addEventListener", text)

# For variables that are addEventListeners
text = re.sub(r"(executeWorkflowForm\.addEventListener)", r"if(executeWorkflowForm) {\n\1", text)
# Close the block
text = re.sub(r"(execModal\.classList\.remove\('active'\);\n\}\);)", r"\1\n}", text)

with open('frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('Patched event listeners globally')
