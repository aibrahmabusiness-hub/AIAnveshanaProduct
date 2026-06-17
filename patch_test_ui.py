import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\components\NodeConfigForm.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add states for testing
content = content.replace("const [connections, setConnections] = useState<any[]>([]);", 
"""const [connections, setConnections] = useState<any[]>([]);
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);""")

# Add test step handler
content = content.replace("const handleChange = (fieldName: string, value: any) => {", 
"""const handleTestStep = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const { post } = await import('../hooks/useApi').then(m => m.default());
      // Wait, we are already using get inside NodeConfigForm, we can just grab post from useApi!
      // But useApi is a hook, so we need to grab post from it at the top of the component.
    } catch(e) {}
  };

  const handleChange = (fieldName: string, value: any) => {""")

# We already use `useApi` in `NodeConfigForm.tsx`: `const { get } = useApi();`. We should also destructure `post`.
content = content.replace("const { get } = useApi();", "const { get, post } = useApi();")

test_function_full = """const handleTestStep = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const data = await post('/api/workflows/test_node', {
        piece_name: pieceName,
        action_name: config['action_name'] || 'send_email', // fallback, should be set
        config: config,
        connection_id: config['connection_id']
      });
      setTestResult(data);
    } catch (err) {
      setTestResult({ success: false, error: String(err) });
    } finally {
      setTesting(false);
    }
  };"""

content = re.sub(r'const handleTestStep = async \(\) => \{.*?} catch\(e\) \{\}\s*};', test_function_full, content, flags=re.DOTALL)

# Add Test button and Debug Panel
render_old = """        </div>
      ))}
    </div>
  );
}"""

render_new = """        </div>
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
          <div className="mt-4 bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
            <div className={`px-4 py-2 text-xs font-semibold uppercase ${testResult.success ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'}`}>
              {testResult.success ? 'Test Successful' : 'Test Failed'}
            </div>
            <div className="p-4 overflow-x-auto">
              <pre className="text-xs font-mono text-slate-300">
                {JSON.stringify(testResult.output || testResult.error || testResult, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}"""

content = content.replace(render_old, render_new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
