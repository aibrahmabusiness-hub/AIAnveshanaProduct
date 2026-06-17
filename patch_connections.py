import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\components\NodeConfigForm.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add connections state
content = content.replace("const [error, setError] = useState<string | null>(null);", 
"""const [error, setError] = useState<string | null>(null);
  const [connections, setConnections] = useState<any[]>([]);""")

# Update fetch to include connections
fetch_old = """        const data = await get(`/api/nodes/schema/${pieceName}`);
        
        if (data.error) {
          setError(data.error);
        } else {
          setSchema({
            schema: data,
          });
        }"""
fetch_new = """        const [schemaData, connectionsData] = await Promise.all([
          get(`/api/nodes/schema/${pieceName}`),
          get(`/api/credentials/${pieceName}/accounts`).catch(() => [])
        ]);
        
        if (schemaData.error) {
          setError(schemaData.error);
        } else {
          setSchema({ schema: schemaData });
          setConnections(Array.isArray(connectionsData) ? connectionsData : []);
        }"""
content = content.replace(fetch_old, fetch_new)

# Add Connection Dropdown rendering
render_old = """  return (
    <div className="space-y-4">"""
render_new = """  return (
    <div className="space-y-4">
      {connections.length > 0 && (
        <div className="p-3 border border-indigo-800/50 rounded-xl bg-indigo-950/20">
          <div className="space-y-2">
            <label className="block text-sm text-indigo-300 font-medium">
              Connection / Authentication
            </label>
            <select
              value={config['connection_id'] || ''}
              onChange={(e) => handleChange('connection_id', e.target.value ? Number(e.target.value) : undefined)}
              className="w-full rounded-xl border border-indigo-700/50 bg-slate-950 px-3 py-2 text-slate-100 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              <option value="">Select an account...</option>
              {connections.map((conn) => (
                <option key={conn.id} value={conn.id}>
                  {conn.name || `Account #${conn.id}`}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}"""
content = content.replace(render_old, render_new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
