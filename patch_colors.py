import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\components\NodeConfigForm.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace object wrapper
content = content.replace('className="border border-slate-700 rounded-lg p-3 space-y-3 bg-slate-900"',
                          'className="border border-slate-200 rounded-lg p-3 space-y-3 bg-slate-50"')

# Replace dynamic JSON text area
content = content.replace('className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 resize-none font-mono text-xs"',
                          'className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none font-mono text-xs"')

# Replace fallback input
content = content.replace('className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400"',
                          'className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"')

# Replace field wrapper
content = content.replace('className="p-3 border border-slate-800 rounded-xl bg-slate-950/50"',
                          'className="p-3 border border-slate-200 rounded-xl bg-white shadow-sm"')

# Replace test result wrapper
content = content.replace('className="mt-4 bg-slate-950 rounded-xl border border-slate-800 overflow-hidden"',
                          'className="mt-4 bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm"')

content = content.replace("testResult.success ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'",
                          "testResult.success ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'")

# Replace Test Button color to emerald
content = content.replace('bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500',
                          'bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500')

# Also fix the text-slate-300 in test results
content = content.replace('className="text-xs font-mono text-slate-300"',
                          'className="text-xs font-mono text-slate-700"')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
