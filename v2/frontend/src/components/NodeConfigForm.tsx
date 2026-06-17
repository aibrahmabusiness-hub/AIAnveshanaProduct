import { useState, useEffect } from 'react';
import useApi from '../hooks/useApi';
import CronBuilder from './CronBuilder';

interface NodeConfigFormProps {
  variables?: {name: string}[];
  pieceName: string;
  config: Record<string, any>;
  projectId?: string;
  onConfigChange: (newConfig: Record<string, any>) => void;
}

interface SchemaProperty {
  type: string;
  description?: string;
  enum?: any[];
  items?: SchemaProperty;
  properties?: Record<string, SchemaProperty>;
  required?: string[];
  default?: any;
  format?: string;
  anyOf?: any[];
}

interface PieceSchema {
  schema: {
    properties: Record<string, SchemaProperty>;
    required?: string[];
  };
}


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
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded-lg shadow-xl max-h-48 overflow-y-auto">
          <div className="p-1 text-xs font-semibold text-slate-500 bg-slate-50 border-b border-slate-200">Available Variables</div>
          {filteredVars.map((v: any) => (
            <div 
              key={v.name} 
              className="px-3 py-2 text-sm text-slate-700 hover:bg-blue-50 cursor-pointer transition-colors"
              onClick={() => handleSelect(v.name)}
            >
              <span className="text-blue-500 font-mono text-xs mr-2">{`{{${v.name}}}`}</span>
              {v.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function NodeConfigForm({ pieceName, config, variables = [], projectId, onConfigChange }: NodeConfigFormProps) {
  const { get, post } = useApi();
  const [schema, setSchema] = useState<PieceSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connections, setConnections] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    const fetchSchema = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const baseAppName = pieceName.split('_')[0];

        if (pieceName === 'ai_agent') {
          // For AI Agent, fetch schema + all agents from all projects
          const schemaData = await get(`/api/nodes/schema/${pieceName}`);
          if (schemaData.error) {
            setError(schemaData.error);
          } else {
            setSchema({ schema: schemaData });
          }
          // Fetch agents: try current project first, then fall back to all
          try {
            const agentsData = await get(`/api/projects/${projectId}/agents`);
            setAgents(agentsData?.agents || []);
          } catch {
            setAgents([]);
          }
        } else {
          const [schemaData, connectionsData] = await Promise.all([
            get(`/api/nodes/schema/${pieceName}`),
            get(`/api/credentials/${baseAppName}/accounts`).catch(() => [])
          ]);
          
          if (schemaData.error) {
            setError(schemaData.error);
          } else {
            setSchema({ schema: schemaData });
            setConnections(connectionsData?.connections && Array.isArray(connectionsData.connections) ? connectionsData.connections : (Array.isArray(connectionsData) ? connectionsData : []));
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    if (pieceName) {
      fetchSchema();
    }
  }, [pieceName, get]);

  const handleTestStep = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const baseAppName = pieceName.split('_')[0];
      const actionName = pieceName.includes('_') ? pieceName.substring(pieceName.indexOf('_') + 1) : 'default';
      const data = await post('/api/workflows/test_node', {
        piece_name: baseAppName,
        action_name: actionName,
        config: config,
        connection_id: config['connection_id'],
        variables: variables
      });
      setTestResult(data);
    } catch (err) {
      setTestResult({ success: false, error: String(err) });
    } finally {
      setTesting(false);
    }
  };

  const handleChange = (fieldName: string, value: any) => {
    const newConfig = { ...config, [fieldName]: value };
    onConfigChange(newConfig);
  };

  const renderField = (fieldName: string, property: SchemaProperty) => {
    const isRequired = schema?.schema.required?.includes(fieldName);
    const fieldValue = config[fieldName] ?? property.default ?? '';

    if (fieldName === 'agent_id') {
      return (
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-slate-700">
            Select Agent
            {isRequired && <span className="text-red-500 ml-1">*</span>}
          </label>
          {agents.length === 0 ? (
            <p className="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
              No agents found in this project. Create an agent first.
            </p>
          ) : (
            <select
              value={fieldValue as string || ''}
              onChange={(e) => handleChange(fieldName, e.target.value ? parseInt(e.target.value) : '')}
              className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">— Select an Agent —</option>
              {agents.map((agent: any) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name}{agent.description ? ` — ${agent.description.slice(0, 40)}` : ''}
                </option>
              ))}
            </select>
          )}
          <p className="text-xs text-slate-500">The agent that will receive and process the query.</p>
        </div>
      );
    }

    // Dynamic visibility for Logic Loop
    if (pieceName === 'logic_loop') {
      const loopType = config['loop_type'] || 'Array / Object';
      if (fieldName === 'array_field' && loopType === 'Number') return null;
      if (fieldName === 'number_iterations' && loopType === 'Array / Object') return null;
    }



    if (fieldName === 'cron' || property.format === 'cron') {
      return (
        <div className="space-y-2">
          <label className="block text-sm text-slate-400">
            {fieldName}
            {isRequired && <span className="text-red-500 ml-1">*</span>}
          </label>
          <CronBuilder
            value={fieldValue}
            onChange={(val: string) => handleChange(fieldName, val)}
          />
          {property.description && (
            <p className="text-xs text-slate-500">{property.description}</p>
          )}
        </div>
      );
    }

    // Extract type from anyOf if needed
    let pType = property.type;
    if (!pType && property.anyOf) {
      const stringType = (property.anyOf as any[]).find(a => a.type === 'string');
      if (stringType) pType = 'string';
    }

    switch (pType) {
      case 'string':
        if (property.enum) {
          return (
            <div className="space-y-2">
              <label className="block text-sm text-slate-400">
                {fieldName}
                {isRequired && <span className="text-red-500 ml-1">*</span>}
              </label>
              <select
                value={fieldValue as string || ''}
                onChange={(e) => handleChange(fieldName, e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">{`Select ${fieldName}`}</option>
                {property.enum.map((enumValue) => (
                  <option key={enumValue} value={enumValue}>
                    {enumValue}
                  </option>
                ))}
              </select>
              {property.description && (
                <p className="text-xs text-slate-500">{property.description}</p>
              )}
            </div>
          );
        }
        return (
          <div className="space-y-2">
            <label className="block text-sm text-slate-400">
              {fieldName}
              {isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            <AutocompleteInput
              type={property.format === 'password' ? 'password' : 'text'}
              value={fieldValue}
              onChange={(val: string) => handleChange(fieldName, val)}
              variables={variables}
              placeholder={property.description || `Enter ${fieldName} (Type @ to select variable)`}
              className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {property.description && (
              <p className="text-xs text-slate-500">{property.description}</p>
            )}
          </div>
        );

      case 'number':
      case 'integer':
        return (
          <div className="space-y-2">
            <label className="block text-sm text-slate-400">
              {fieldName}
              {isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type="number"
              value={fieldValue}
              onChange={(e) => handleChange(fieldName, Number(e.target.value))}
              placeholder={property.description || `Enter ${fieldName}`}
              className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            {property.description && (
              <p className="text-xs text-slate-500">{property.description}</p>
            )}
          </div>
        );

      case 'boolean':
        return (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-400">
                {fieldName}
                {isRequired && <span className="text-red-500 ml-1">*</span>}
              </label>
              <input
                type="checkbox"
                checked={fieldValue as boolean || false}
                onChange={(e) => handleChange(fieldName, e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 bg-white text-blue-600 focus:ring-blue-500"
              />
            </div>
            {property.description && (
              <p className="text-xs text-slate-500">{property.description}</p>
            )}
          </div>
        );

      case 'array':
        if (property.items?.type === 'string') {
          return (
            <div className="space-y-2">
              <label className="block text-sm text-slate-400">
                {fieldName}
                {isRequired && <span className="text-red-500 ml-1">*</span>}
              </label>
              <AutocompleteInput
                isTextArea={true}
                value={Array.isArray(fieldValue) ? fieldValue.join('\n') : (typeof fieldValue === 'string' ? fieldValue : '')}
                onChange={(val: string) => handleChange(fieldName, val.split('\n').filter(Boolean))}
                variables={variables}
                placeholder={property.description || `Enter ${fieldName} (one per line) (Type @ to select variable)`}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {property.description && (
                <p className="text-xs text-slate-500">{property.description}</p>
              )}
            </div>
          );
        }
        return null;

      case 'object':
        if (property.properties) {
          return (
            <div className="space-y-2">
              <label className="block text-sm text-slate-400">
                {fieldName}
                {isRequired && <span className="text-red-500 ml-1">*</span>}
              </label>
              <div className="border border-slate-200 rounded-lg p-3 space-y-3 bg-slate-50">
                {Object.entries(property.properties).map(([subFieldName, subProperty]) => (
                  <div key={subFieldName} className="space-y-1">
                    <label className="block text-xs text-slate-500">
                      {subFieldName}
                      {property.required?.includes(subFieldName) && <span className="text-red-500 ml-1">*</span>}
                    </label>
                    <AutocompleteInput
                      type="text"
                      value={(fieldValue as Record<string, any>)?.[subFieldName] ?? ''}
                      onChange={(val: string) => {
                        const newValue = { ...(fieldValue as Record<string, any> | {}), [subFieldName]: val };
                        handleChange(fieldName, newValue);
                      }}
                      variables={variables}
                      className="w-full rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs text-slate-800"
                    />
                  </div>
                ))}
              </div>
              {property.description && (
                <p className="text-xs text-slate-500">{property.description}</p>
              )}
            </div>
          );
        }
        return null;

      default:
        return (
          <div className="space-y-2">
            <label className="block text-sm text-slate-400">
              {fieldName}
              {isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            <textarea
              value={JSON.stringify(fieldValue, null, 2)}
              onChange={(e) => {
                try {
                  handleChange(fieldName, JSON.parse(e.target.value));
                } catch {
                  // Keep previous value if invalid JSON
                }
              }}
              placeholder={`Raw JSON for ${fieldName}`}
              rows={4}
              className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none font-mono text-xs"
            />
            {property.description && (
              <p className="text-xs text-slate-500">{property.description}</p>
            )}
          </div>
        );
    }
  };

  if (loading) {
    return <p className="text-sm text-slate-500">Loading configuration schema...</p>;
  }

  if (error) {
    return <p className="text-sm text-red-500">{error}</p>;
  }

  if (!schema || !schema.schema.properties || Object.keys(schema.schema.properties).length === 0) {
    return <p className="text-sm text-slate-500">No configuration fields for this piece.</p>;
  }

  return (
    <div className="space-y-4">
      {pieceName !== 'manual' && pieceName !== 'webhook' && pieceName !== 'schedule' && pieceName !== 'logic_loop' && pieceName !== 'condition' && pieceName !== 'delay' && pieceName !== 'ai_agent' && (

        <div className="p-3 border border-indigo-800/50 rounded-xl bg-indigo-950/20">
          <div className="space-y-2">
            <label className="block text-sm text-indigo-300 font-medium">
              Connection / Authentication
            </label>
              <select
                value={config['connection_id'] || ''}
                onChange={(e) => {
                  if (e.target.value === 'ADD_NEW') {
                    window.open('/project.html', '_blank');
                    return;
                  }
                  handleChange('connection_id', e.target.value ? e.target.value : undefined);
                }}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select an account...</option>
                {connections.map((conn) => (
                  <option key={conn.id} value={conn.id}>
                    {conn.name || `Account #${conn.id}`}
                  </option>
                ))}
                <option value="ADD_NEW" className="text-blue-600 font-bold">+ Add New Connection...</option>
              </select>
          </div>
        </div>
      )}
      {Object.entries(schema.schema.properties).map(([fieldName, property]) => (
        <div key={fieldName} className="p-3 border border-slate-200 rounded-xl bg-white shadow-sm">
          {renderField(fieldName, property)}
        </div>
      ))}
      
      {/* Test Step UI */}
      <div className="pt-4 mt-6 border-t border-slate-800">
        <button
          onClick={handleTestStep}
          disabled={testing}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {testing ? 'Testing...' : 'Test Step'}
        </button>
        
        {testResult && (
          <div className="mt-4 bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
            <div className={`px-4 py-2 text-xs font-semibold uppercase ${testResult.success ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
              {testResult.success ? 'Test Successful' : 'Test Failed'}
            </div>
            <div className="p-4 overflow-x-auto">
              <pre className="text-xs font-mono text-slate-700">
                {JSON.stringify(testResult.output || testResult.error || testResult, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
