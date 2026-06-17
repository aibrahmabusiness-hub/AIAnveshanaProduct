import re

filepath = r"c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\components\NodeConfigForm.tsx"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add agents state
content = content.replace(
    "const [connections, setConnections] = useState<any[]>([]);",
    "const [connections, setConnections] = useState<any[]>([]);\n  const [agents, setAgents] = useState<any[]>([]);"
)

# 2. Update useEffect to fetch agents
old_fetch = """          const [schemaData, connectionsData] = await Promise.all([
            get(`/api/nodes/schema/${pieceName}`),
            get(`/api/connections?app=${baseAppName}`)
          ]);
          setSchema(schemaData as PieceSchema);
          setConnections((connectionsData as any)?.connections || []);"""

new_fetch = """          const [schemaData, connectionsData, agentsData] = await Promise.all([
            get(`/api/nodes/schema/${pieceName}`),
            get(`/api/connections?app=${baseAppName}`),
            get(`/api/agents`).catch(() => ({ agents: [] }))
          ]);
          setSchema(schemaData as PieceSchema);
          setConnections((connectionsData as any)?.connections || []);
          setAgents((agentsData as any)?.agents || []);"""

content = content.replace(old_fetch, new_fetch)

# 3. Add fieldName === 'agent_id' check to renderField
old_render_start = """  const renderField = (fieldName: string, property: SchemaProperty) => {
    // Dynamic visibility for Logic Loop"""

new_render_start = """  const renderField = (fieldName: string, property: SchemaProperty) => {
    const isRequired = schema?.schema.required?.includes(fieldName);
    const fieldValue = config[fieldName] ?? property.default ?? '';

    if (fieldName === 'agent_id') {
      return (
        <div className="space-y-2">
          <label className="block text-sm text-slate-400">
            {fieldName}
            {isRequired && <span className="text-red-500 ml-1">*</span>}
          </label>
          <select
            value={fieldValue as string || ''}
            onChange={(e) => handleChange(fieldName, parseInt(e.target.value))}
            className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">{`Select an Agent`}</option>
            {agents.map((agent: any) => (
              <option key={agent.id} value={agent.id}>
                {agent.name}
              </option>
            ))}
          </select>
          {property.description && (
            <p className="text-xs text-slate-500">{property.description}</p>
          )}
        </div>
      );
    }

    // Dynamic visibility for Logic Loop"""

content = content.replace(old_render_start, new_render_start)

# We also need to fix the duplicate isRequired and fieldValue that are defined later
old_redundant = """    const fieldValue = config[fieldName] ?? property.default ?? '';
    const isRequired = schema?.schema.required?.includes(fieldName);"""

content = content.replace(old_redundant, "")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("NodeConfigForm.tsx patched successfully.")
