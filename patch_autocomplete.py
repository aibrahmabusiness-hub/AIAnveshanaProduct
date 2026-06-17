import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\components\NodeConfigForm.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add variables prop
content = content.replace("interface NodeConfigFormProps {", 
"""interface NodeConfigFormProps {
  variables?: {name: string}[];""")

content = content.replace("export default function NodeConfigForm({ pieceName, config, onConfigChange }: NodeConfigFormProps) {", 
"export default function NodeConfigForm({ pieceName, config, variables = [], onConfigChange }: NodeConfigFormProps) {")


# Inject Autocomplete component
autocomplete_code = """
function AutocompleteInput({ value, onChange, variables, placeholder, className, type = 'text', isTextArea = false }: any) {
  const [show, setShow] = useState(false);
  const [filter, setFilter] = useState('');
  
  const handleInput = (e: any) => {
    const val = e.target.value;
    onChange(val);
    
    // Check if we just typed @
    const lastAt = val.lastIndexOf('@');
    if (lastAt !== -1) {
      const textAfterAt = val.substring(lastAt + 1);
      if (!textAfterAt.includes(' ')) {
        setFilter(textAfterAt.toLowerCase());
        setShow(true);
        return;
      }
    }
    setShow(false);
  };
  
  const handleSelect = (varName: string) => {
    const lastAt = value.lastIndexOf('@');
    if (lastAt !== -1) {
      const newVal = value.substring(0, lastAt) + `{{${varName}}}` + value.substring(lastAt + filter.length + 1);
      onChange(newVal);
    }
    setShow(false);
  };

  const filteredVars = variables.filter((v: any) => v.name.toLowerCase().includes(filter));

  return (
    <div className="relative w-full">
      {isTextArea ? (
        <textarea
          value={value}
          onChange={handleInput}
          placeholder={placeholder}
          rows={3}
          className={className + " resize-none"}
        />
      ) : (
        <input
          type={type}
          value={value}
          onChange={handleInput}
          placeholder={placeholder}
          className={className}
        />
      )}
      {show && filteredVars.length > 0 && (
        <div className="absolute z-50 mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg shadow-xl max-h-48 overflow-y-auto">
          <div className="p-1 text-xs font-semibold text-slate-400 bg-slate-900 border-b border-slate-700">Available Variables</div>
          {filteredVars.map((v: any) => (
            <div 
              key={v.name} 
              className="px-3 py-2 text-sm text-slate-200 hover:bg-indigo-600 cursor-pointer transition-colors"
              onClick={() => handleSelect(v.name)}
            >
              <span className="text-indigo-300 font-mono text-xs mr-2">{{`{{${v.name}}}`}}</span>
              {v.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
"""

content = content.replace("export default function NodeConfigForm", autocomplete_code + "\nexport default function NodeConfigForm")

# Replace inputs with AutocompleteInput
content = content.replace("""<input
              type={property.format === 'password' ? 'password' : 'text'}
              value={fieldValue}
              onChange={(e) => handleChange(fieldName, e.target.value)}
              placeholder={property.description || `Enter ${fieldName}`}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400"
            />""", 
"""<AutocompleteInput
              type={property.format === 'password' ? 'password' : 'text'}
              value={fieldValue}
              onChange={(val: string) => handleChange(fieldName, val)}
              variables={variables}
              placeholder={property.description || `Enter ${fieldName}`}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400"
            />""")

content = content.replace("""<textarea
                value={(fieldValue as string[] | undefined)?.join('\\n') || ''}
                onChange={(e) => handleChange(fieldName, e.target.value.split('\\n').filter(Boolean))}
                placeholder={property.description || `Enter ${fieldName} (one per line)`}
                rows={3}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 resize-none"
              />""",
"""<AutocompleteInput
                isTextArea={true}
                value={(fieldValue as string[] | undefined)?.join('\\n') || ''}
                onChange={(val: string) => handleChange(fieldName, val.split('\\n').filter(Boolean))}
                variables={variables}
                placeholder={property.description || `Enter ${fieldName} (one per line)`}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400"
              />""")

content = content.replace("""<input
                      type="text"
                      value={(fieldValue as Record<string, any>)?.[subFieldName] ?? ''}
                      onChange={(e) => {
                        const newValue = { ...(fieldValue as Record<string, any> | {}), [subFieldName]: e.target.value };
                        handleChange(fieldName, newValue);
                      }}
                      className="w-full rounded-lg border border-slate-800 bg-slate-950 px-2 py-1 text-xs text-slate-100"
                    />""",
"""<AutocompleteInput
                      type="text"
                      value={(fieldValue as Record<string, any>)?.[subFieldName] ?? ''}
                      onChange={(val: string) => {
                        const newValue = { ...(fieldValue as Record<string, any> | {}), [subFieldName]: val };
                        handleChange(fieldName, newValue);
                      }}
                      variables={variables}
                      className="w-full rounded-lg border border-slate-800 bg-slate-950 px-2 py-1 text-xs text-slate-100"
                    />""")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
