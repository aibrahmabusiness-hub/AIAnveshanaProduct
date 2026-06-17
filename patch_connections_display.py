import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\components\NodeConfigForm.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Change connection render logic
render_old = """  return (
    <div className="space-y-4">
      {connections.length > 0 && ("""

render_new = """  return (
    <div className="space-y-4">
      {pieceName !== 'manual' && pieceName !== 'webhook' && pieceName !== 'schedule' && (
"""
content = content.replace(render_old, render_new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
