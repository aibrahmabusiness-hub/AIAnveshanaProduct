const express = require('express');
const app = express();
app.use(express.json());

// Load the activepieces packages
const gmail = require('@activepieces/piece-gmail').gmail;
// Inject missing action names so validation passes for our custom python tools
if (!gmail._actions) gmail._actions = {};
gmail._actions['read_email'] = { name: 'read_email', displayName: 'Read Email' };
gmail._actions['search_email'] = { name: 'search_email', displayName: 'Search Email' };
gmail._actions['send_email'] = { name: 'send_email', displayName: 'Send Email' };
gmail._actions['gmail_send_email'] = { name: 'gmail_send_email', displayName: 'Send Email' };
gmail._actions['gmail_read_email'] = { name: 'gmail_read_email', displayName: 'Read Email' };
gmail._actions['gmail_search_email'] = { name: 'gmail_search_email', displayName: 'Search Email' };

// Load custom mocked packages
const { jira, servicenow, coreLogic } = require('./customPieces');

// Placeholders for Salesforce to satisfy piece/action checks
const salesforcePiece = {
    displayName: 'Salesforce',
    _actions: {
        query: { name: 'query', displayName: 'Query SOQL' },
        create: { name: 'create', displayName: 'Create Record' }
    }
};

const pieces = {
    '@activepieces/piece-gmail': gmail,
    'gmail': gmail,
    '@activepieces/piece-jira': jira,
    'jira': jira,
    '@activepieces/piece-servicenow': servicenow,
    'servicenow': servicenow,
    '@activepieces/piece-salesforce': salesforcePiece,
    'salesforce': salesforcePiece,
    'core': coreLogic,
    'ai_agent': { displayName: 'AI Agent', _actions: { execute: { name: 'execute', displayName: 'Execute' } } }
};

app.get('/pieces', (req, res) => {
    const metadataMap = new Map();
    
    Object.keys(pieces).forEach(name => {
        const piece = pieces[name];
        if (!piece) return;
        const displayName = piece.displayName || name;
        const isScoped = name.startsWith('@');
        
        // Deduplicate: if we already added a piece with this displayName
        if (metadataMap.has(displayName)) {
            // Keep the scoped name version (starts with @) in preference to short names
            if (isScoped) {
                metadataMap.set(displayName, {
                    name: name,
                    displayName: piece.displayName,
                    logoUrl: piece.logoUrl || '',
                    actions: Object.keys(piece._actions || {}).map(actionName => {
                        const action = piece._actions[actionName];
                        return {
                            name: actionName,
                            displayName: action.displayName,
                            description: action.description || '',
                            props: action.props || {}
                        }
                    })
                });
            }
        } else {
            metadataMap.set(displayName, {
                name: name,
                displayName: piece.displayName,
                logoUrl: piece.logoUrl || '',
                actions: Object.keys(piece._actions || {}).map(actionName => {
                    const action = piece._actions[actionName];
                    return {
                        name: actionName,
                        displayName: action.displayName,
                        description: action.description || '',
                        props: action.props || {}
                    }
                })
            });
        }
    });
    
    res.json(Array.from(metadataMap.values()));
});

// Helper for interpolation
function interpolate(value, context) {
    if (typeof value === 'string') {
        // If the entire string is just one variable e.g. "{{variable}}", return the object directly!
        const exactMatch = value.match(/^\{\{\s*(.+?)\s*\}\}$/);
        if (exactMatch) {
            let current = context;
            for (const part of exactMatch[1].split('.')) {
                if (current == null) return value;
                current = current[part];
            }
            return current !== undefined ? current : value;
        }

        // Otherwise replace within the string
        return value.replace(/\{\{\s*(.+?)\s*\}\}/g, (match, path) => {
            let current = context;
            for (const part of path.split('.')) {
                if (current == null) return match;
                current = current[part];
            }
            return current !== undefined ? (typeof current === 'object' ? JSON.stringify(current) : current) : match;
        });
    } else if (Array.isArray(value)) {
        return value.map(v => interpolate(v, context));
    } else if (value !== null && typeof value === 'object') {
        const result = {};
        for (const [k, v] of Object.entries(value)) {
            result[k] = interpolate(v, context);
        }
        return result;
    }
    return value;
}

const cancelledTasks = new Set();
const cancelledWorkflows = new Set();

app.post('/stop_workflow', (req, res) => {
    if (req.body.task_id) {
        cancelledTasks.add(req.body.task_id);
    }
    if (req.body.workflow_id) {
        cancelledWorkflows.add(req.body.workflow_id);
    }
    res.json({ success: true });
});

// Full workflow execution endpoint
app.post('/execute_workflow', async (req, res) => {
    const { nodes, edges, initialData, steps, task_id, workflow_id } = req.body;
    
    // Clear the workflow cancellation flag if it's a new run
    if (workflow_id) {
        cancelledWorkflows.delete(workflow_id);
    }
    
    // Support legacy "steps" fallback if backend hasn't upgraded
    const flowNodes = nodes || steps || [];
    const flowEdges = edges || [];
    
    const context = { trigger: initialData || {} };
    if (initialData) {
        for (const [k, v] of Object.entries(initialData)) {
            context[k] = v;
        }
    }
    const logs = [];
    
    // Build adjacency list for edges: fromNodeId -> [{ target, handle }]
    const adj = {};
    for (const edge of flowEdges) {
        if (!adj[edge.source]) adj[edge.source] = [];
        adj[edge.source].push({ target: edge.target, handle: edge.sourceHandle });
    }
    
    const nodeMap = {};
    const inDegree = {};
    for (const n of flowNodes) {
        nodeMap[n.id] = n;
        inDegree[n.id] = 0;
    }
    
    for (const edge of flowEdges) {
        if (nodeMap[edge.target] && nodeMap[edge.source]) {
            inDegree[edge.target]++;
        }
    }
    
    // Execution queue
    const queue = [];
    // Start with nodes with inDegree 0
    for (const n of flowNodes) {
        if (inDegree[n.id] === 0 && !n.type?.startsWith('trigger')) {
            queue.push({ nodeId: n.id, scopeContext: { ...context } });
        }
    }
    
    // Fallback: if queue is empty but nodes exist (circular dependencies or no roots without triggers)
    if (queue.length === 0 && flowNodes.length > 0) {
        for (const n of flowNodes) {
            if (!n.type?.startsWith('trigger')) {
                queue.push({ nodeId: n.id, scopeContext: { ...context } });
                break; // Just start from the first one
            }
        }
    }
    
    let lastScopeContext = context;
    let stepCount = 0;
    const MAX_STEPS = 1000;
    
    async function pushQueue(edge, scopeContext) {
        if (req.body.webhookUrl && edge && edge.id) {
            try {
                await fetch(req.body.webhookUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: 'edge_execute', edge_id: edge.id })
                });
            } catch(e) {}
        }
        queue.push({ nodeId: edge.target, scopeContext });
    }
    
    while (queue.length > 0) {
        if (stepCount++ > MAX_STEPS) {
            logs.push({
                step: 'system',
                success: false,
                error: `Execution limit exceeded (${MAX_STEPS} steps). Infinite loop detected in graph.`,
                duration: 0,
                inputs: {},
                result: null
            });
            break;
        }

        if ((task_id && cancelledTasks.has(task_id)) || (workflow_id && cancelledWorkflows.has(workflow_id))) {
            logs.push({
                step: 'system',
                success: false,
                error: 'Workflow was stopped by user.',
                duration: 0,
                inputs: {},
                result: null
            });
            break;
        }

        const { nodeId, scopeContext } = queue.shift();
        lastScopeContext = scopeContext;
        const step = nodeMap[nodeId];
        if (!step) continue;
        
        let pieceName = step.piece_name || step.data?.piece || 'core';
        let actionName = step.action_name || step.data?.action || '';
        
        // Split piece_name if it contains action (e.g. gmail_send_email), but don't split ai_agent
        if (pieceName.includes('_') && !pieceName.startsWith('@') && !step.data?.action && pieceName !== 'ai_agent') {
            const parts = pieceName.split('_');
            pieceName = parts[0];
            actionName = parts.slice(1).join('_');
        }
        
        // Force actionName for ai_agent since the frontend might not pass one
        if (pieceName === 'ai_agent' && !actionName) {
            actionName = 'execute';
        }
        
        // Handle legacy steps format parsing
        if (!step.piece_name && !step.data?.piece && step.type && step.type.includes('::')) {
            const parts = step.type.split('::');
            pieceName = parts[0];
            actionName = parts[1];
        }
        
        let success = true;
        let result = null;
        let error = null;
        let duration = 0;
        let inputs = {};
        
        if (req.body.webhookUrl) {
            try {
                await fetch(req.body.webhookUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: 'node_start', node_id: nodeId, node_label: step.data?.label || nodeId })
                });
            } catch(e) {}
        }
        
        if ((pieceName === 'core' && actionName === 'branch') || pieceName === 'condition') {
            const configObj = step.data?.config || step.data || {};
            const val = interpolate(configObj.condition, scopeContext);
            inputs = { condition: val };
            let conditionMet = false;
            if (val === 'true' || val === true) conditionMet = true;
            result = { conditionMet, rawInput: val };
            
            const nextEdges = adj[nodeId] || [];
            for (const e of nextEdges) {
                if (conditionMet && (e.handle === 'true' || !e.handle)) {
                    await pushQueue(e, { ...scopeContext, [step.id]: result });
                } else if (!conditionMet && (e.handle === 'false')) {
                    await pushQueue(e, { ...scopeContext, [step.id]: result });
                }
            }
        } 
        else if (pieceName === 'logic' && actionName === 'loop') {
             const configObj = step.data?.config || step.data || {};
             let loopType = configObj.loop_type || 'Array / Object';
             let arrayVal = [];
             
             if (loopType === 'Number') {
                 let total = parseInt(interpolate(configObj.number_iterations, scopeContext)) || 0;
                 for (let i = 0; i < total; i++) arrayVal.push(i + 1);
             } else {
                 console.log('Loop Array Field Config:', configObj.array_field);
                 arrayVal = interpolate(configObj.array_field, scopeContext);
                 console.log('Loop Array Val After Interpolate:', typeof arrayVal, arrayVal);
                 if (typeof arrayVal === 'string') {
                     try { arrayVal = JSON.parse(arrayVal); } catch (e) {}
                 }
                 if (!Array.isArray(arrayVal)) {
                     if (typeof arrayVal === 'object' && arrayVal !== null) {
                         arrayVal = Object.entries(arrayVal).map(([k, v]) => ({ key: k, value: v }));
                     } else {
                         arrayVal = [];
                     }
                 }
             }
             
             inputs = { loop_type: loopType, items: arrayVal };
             result = { looped: true, total: arrayVal.length };
             
             const nextEdges = adj[nodeId] || [];
             
             // Push loop branches
             for (let i = 0; i < arrayVal.length; i++) {
                 const item = arrayVal[i];
                 const loopContext = { ...scopeContext, loop: { item, index: i } };
                 loopContext[step.id] = { item, index: i };
                 
                 for (const e of nextEdges) {
                     if (e.handle === 'loop') {
                         await pushQueue(e, loopContext);
                     }
                 }
             }
             
             // Push done branch
             for (const e of nextEdges) {
                 if (e.handle === 'done') {
                     await pushQueue(e, { ...scopeContext, [step.id]: result });
                 }
             }
        }
        else if (['manual', 'schedule', 'webhook'].includes(pieceName) || pieceName.startsWith('trigger')) {
            // Triggers (manual, schedule, etc) auto-succeed in the execution phase
            result = inputs;
            const nextEdges = adj[nodeId] || [];
            for (const e of nextEdges) {
                await pushQueue(e, { ...scopeContext, [step.id]: result });
            }
        }
        else {
            // Normal Node Execution
            const piece = pieces[pieceName] || pieces[`@activepieces/piece-${pieceName}`];
            if (!piece) {
                success = false;
                error = `Piece ${pieceName} not found`;
            } else {
                let action = undefined;
                if (Array.isArray(piece.actions)) {
                    action = piece.actions.find(a => a.name === actionName);
                } else if (piece.actions && typeof piece.actions === 'object') {
                    action = piece.actions[actionName];
                } else if (piece._actions && piece._actions[actionName]) {
                    action = piece._actions[actionName];
                }
                
                if (!action) {
                    success = false;
                    error = `Action ${actionName} not found in ${pieceName}`;
                } else {
                    try {
                        const interpolatedProps = {};
                        const configObj = step.data?.config || step.data || {};
                        for (const [key, val] of Object.entries(configObj)) {
                            interpolatedProps[key] = interpolate(val, scopeContext);
                        }
                        inputs = interpolatedProps;
                        let normalizedPieceName = pieceName.replace('@activepieces/piece-', '');
                        if (['gmail', 'jira', 'servicenow', 'salesforce', 'ai_agent'].includes(normalizedPieceName)) {
                            const headers = { 'Content-Type': 'application/json' };
                            if (req.headers['authorization']) headers['Authorization'] = req.headers['authorization'];
                            
                            const start = Date.now();
                            const response = await fetch(`http://127.0.0.1:8000/api/tools/execute`, {
                                method: 'POST',
                                headers,
                                body: JSON.stringify({
                                    tool_name: normalizedPieceName,
                                    action_name: actionName,
                                    params: Object.assign({}, inputs)
                                })
                            });
                            
                            const out = await response.json();
                            duration = Date.now() - start;
                            
                            if (out.success) {
                                result = out.output;
                            } else {
                                success = false;
                                error = out.error || "Tool execution failed";
                            }
                        } else {
                            const start = Date.now();
                            result = await action.run({ propsValue: inputs });
                            duration = Date.now() - start;
                        }
                    } catch (err) {
                        success = false;
                        error = err.message;
                    }
                }
            }
            
            // For standard nodes, push all outgoing edges (except specific handles we might define later)
            const nextEdges = adj[nodeId] || [];
            for (const e of nextEdges) {
                await pushQueue(e, { ...scopeContext, [step.id]: result });
            }
        }
        
        logs.push({
            step: step.id,
            success,
            error,
            duration,
            inputs,
            result
        });

        lastScopeContext[step.id] = result;
        lastScopeContext[`${step.id}_output`] = result;

        if (req.body.webhookUrl) {
            try {
                await fetch(req.body.webhookUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        type: success ? 'node_success' : 'node_error', 
                        node_id: nodeId, 
                        result: result, 
                        error: error 
                    })
                });
            } catch(e) {}
        }
    }
    
    if (task_id) {
        cancelledTasks.delete(task_id);
    }
    return res.json({ success: true, logs, context: lastScopeContext });
});

app.listen(3001, () => console.log('Lightweight engine running on 3001'));
