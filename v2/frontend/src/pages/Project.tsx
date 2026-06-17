import { useState, useEffect, useRef, type DragEvent, useCallback } from 'react';

import { ArrowLeft, Plus, Trash2, Play, Square, Save, Loader2, CheckCircle, XCircle, AlertCircle, ChevronDown, ChevronRight, X, Clock, Repeat, GitBranch, Timer, Webhook, Bot } from 'lucide-react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  reconnectEdge,
  Connection,
  useNodesState,
  useEdgesState,
  NodeTypes,
  EdgeTypes,
  Node,
  Edge,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import BaseNode from '../nodes/BaseNode';
import ButtonEdge from '../edges/ButtonEdge';
import NodeConfigForm from '../components/NodeConfigForm';
import ExecutionHistory from '../components/ExecutionHistory';
import DebugPanel from '../components/DebugPanel';
import useApi from '../hooks/useApi';
import { useWorkflowVersion } from '../contexts/WorkflowVersionContext';
import { getWebSocketUrl } from '../config/workflowConfig';
import { NodeExecutionStatus, WorkflowExecutionState, Piece } from '../types/flowTypes';

interface Project {
  id: string;
  name: string;
  nodes: any[];
  edges: any[];
}

  // Workflow pieces are now loaded dynamically from the backend


// Node types for React Flow
const nodeTypes: NodeTypes = {
  customNode: BaseNode,
};

const edgeTypes: EdgeTypes = {
  buttonedge: ButtonEdge,
};

export default function Project() {
  const urlParams = new URLSearchParams(window.location.search);
  const initialId = urlParams.get('id') || 'new_workflow';
  const agentIdParam = urlParams.get('agent_id');
  const agentId = (agentIdParam && agentIdParam !== 'null' && !isNaN(Number(agentIdParam))) ? Number(agentIdParam) : null;
  
  const [id, setId] = useState(initialId);

  // Extract project ID from parent window URL or query params
  let projectId = urlParams.get('project_id') || '';
  if (!projectId) {
    try {
      if (window.parent && window.parent.location.pathname.includes('/project/')) {
        projectId = window.parent.location.pathname.split('/').filter(Boolean).pop() || '';
      }
    } catch (e) {
      console.warn("Could not read parent location:", e);
    }
  }
  
  const navigateBack = () => {
    // If in iframe, send message to parent to close iframe
    if (window.parent !== window) {
      window.parent.postMessage({ type: 'close-v2-editor' }, '*');
    } else {
      window.history.back();
    }
  };
  const { version } = useWorkflowVersion();
  const { get, post, put } = useApi();
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);


  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [searchPiece, setSearchPiece] = useState('');
  const [nodeCounter, setNodeCounter] = useState(0);
  const [nodeStatus, setNodeStatus] = useState<NodeExecutionStatus>({});
  const [edgeExecutionCounts, setEdgeExecutionCounts] = useState<Record<string, number>>({});
  const [activeEdges, setActiveEdges] = useState<Record<string, boolean>>({});
  const [executionState, setExecutionState] = useState<WorkflowExecutionState>({
    isExecuting: false,
    currentNodeId: undefined,
    taskId: undefined,
  });
  const [executionLogs, setExecutionLogs] = useState<{
    message: string;
    timestamp: string;
    type: 'info' | 'success' | 'error';
    nodeId?: string;
    inputs?: any;
    result?: any;
    duration?: number;
  }[]>([]);
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [activeLeftTab, setActiveLeftTab] = useState<'variables' | 'activities' | 'triggers' | 'runs'>('activities');
  const [workflowPieces, setWorkflowPieces] = useState<Piece[]>([]);

  useEffect(() => {
    get('/api/nodes/schema').then(data => {
      if (data && data.nodes) {
        setWorkflowPieces(data.nodes);
      }
    }).catch(e => console.error("Failed to load workflow pieces", e));
  }, []);
  const [isGmailExpanded, setIsGmailExpanded] = useState(true);
  const [isLogicExpanded, setIsLogicExpanded] = useState(true);

  const renderIcon = (piece: Piece) => {
    if (piece.icon) return <img src={piece.icon} alt={piece.displayName} className="w-5 h-5 object-contain" />;
    
    const p = piece.name;
    if (p === 'manual') return <Play className="w-5 h-5 text-emerald-600" />;
    if (p === 'schedule') return <Clock className="w-5 h-5 text-emerald-600" />;
    if (p === 'logic_loop' || p === 'loop') return <Repeat className="w-5 h-5 text-blue-600" />;
    if (p === 'condition') return <GitBranch className="w-5 h-5 text-blue-600" />;
    if (p === 'delay') return <Timer className="w-5 h-5 text-blue-600" />;
    if (p === 'webhook') return <Webhook className="w-5 h-5 text-slate-600" />;
    if (p === 'ai_agent') return <Bot className="w-5 h-5 text-purple-600" />;
    
    // Custom simpleicons URL for others
    const cdnName = p.split('_')[0]; // Extract the base app name (e.g. gmail_read_email -> gmail)
    return <img src={`https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/${cdnName}.svg`} alt={p} className="w-5 h-5 object-contain" onError={(e) => {
      // If icon fails to load, you could set a fallback or hide it
      (e.target as HTMLImageElement).style.display = 'none';
    }} />;
  };

  const [variables, setVariables] = useState<{id: string; name: string; type: string; scope: string; value: string}[]>([]);
  const [initialViewport, setInitialViewport] = useState<any>(null);
  const [newVar, setNewVar] = useState({name: '', type: 'String', scope: 'Input', value: ''});

  
  const styledEdges = edges.map(e => {
    const count = edgeExecutionCounts[e.id];
    const isActive = activeEdges[e.id];
    return {
      ...e,
      animated: isActive || executionState.isExecuting,
      label: count ? count + 'x' : undefined,
      labelBgStyle: { fill: '#f8fafc', color: '#0f172a', fontWeight: 'bold' },
      style: {
        ...e.style,
        stroke: isActive ? '#22c55e' : (count ? '#3b82f6' : '#94a3b8'),
        strokeWidth: isActive || count ? 3 : 2,
      }
    };
  });

  // Initialize WebSocket connection - now uses version-aware URL
  useEffect(() => {
    const wsUrl = getWebSocketUrl(version, id);
    
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected to', wsUrl);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWorkflowEvent(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          if (wsRef.current === ws) {
            // Only reconnect if this is still the current WebSocket
            const newWsUrl = getWebSocketUrl(version, id);
            const newWs = new WebSocket(newWsUrl);
            wsRef.current = newWs;
            newWs.onopen = () => console.log('WebSocket reconnected');
            newWs.onmessage = (event) => {
              try {
                const data = JSON.parse(event.data);
                handleWorkflowEvent(data);
              } catch (err) {
                console.error('Failed to parse WebSocket message:', err);
              }
            };
            newWs.onclose = () => console.log('WebSocket disconnected');
          }
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
    }

    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [id, version]);

  // Handle workflow execution events from WebSocket
  const handleWorkflowEvent = useCallback((data: any) => {
    const eventType = data.type;
    const eventData = data.data || {};
    const workflowId = eventData.workflow_id;
    
    // Only process events for current workflow
    if (workflowId && workflowId !== id) return;

    switch (eventType) {
      case 'workflow_start':
        setExecutionState(prev => ({
          ...prev,
          isExecuting: true,
          taskId: eventData.task_id,
        }));
        setExecutionLogs(prev => [...prev, {
          message: `Workflow started (Task: ${eventData.task_id})`,
          timestamp: new Date().toISOString(),
          type: 'info'
        }]);
        break;

      case 'node_start':
        setNodeStatus(prev => ({
          ...prev,
          [eventData.node_id]: {
            status: 'running',
            message: `Executing ${eventData.node_label || eventData.node_id}...`,
          }
        }));
        setExecutionState(prev => ({
          ...prev,
          currentNodeId: eventData.node_id,
        }));
        setExecutionLogs(prev => [...prev, {
          message: `Started: ${eventData.node_label || eventData.node_id} (${eventData.piece_type})`,
          timestamp: new Date().toISOString(),
          type: 'info'
        }]);
        break;

      case 'node_success':
        setNodeStatus(prev => ({
          ...prev,
          [eventData.node_id]: {
            status: 'success',
            message: `Completed: ${JSON.stringify(eventData.result?.message || eventData.result)}`,
          }
        }));
        setExecutionLogs(prev => [...prev, {
          message: `Success: ${eventData.node_id}`,
          timestamp: new Date().toISOString(),
          type: 'success'
        }]);
        break;

      case 'node_error':
        setNodeStatus(prev => ({
          ...prev,
          [eventData.node_id]: {
            status: 'error',
            error: eventData.error,
          }
        }));
        setExecutionLogs(prev => [...prev, {
          message: `Error: ${eventData.error}`,
          timestamp: new Date().toISOString(),
          type: 'error'
        }]);
        break;

      case 'workflow_complete':
        setExecutionState(prev => ({
          ...prev,
          isExecuting: false,
          currentNodeId: undefined,
        }));
        setNodeStatus({});
          setEdgeExecutionCounts({});
          setActiveEdges({});
        setExecutionLogs(prev => [...prev, {
          message: `Workflow completed! Executed ${Object.keys(eventData.results || {}).length} nodes`,
          timestamp: new Date().toISOString(),
          type: 'success'
        }]);
        break;

      case 'workflow_error':
        setExecutionState(prev => ({
          ...prev,
          isExecuting: false,
          currentNodeId: undefined,
        }));
        setExecutionLogs(prev => [...prev, {
          message: `Workflow failed: ${eventData.error}`,
          timestamp: new Date().toISOString(),
          type: 'error'
        }]);
        break;

      default:
        console.log('Unknown event type:', eventType, eventData);
    }
  }, [id]);

  // Update nodes with execution status
  useEffect(() => {
    if (Object.keys(nodeStatus).length > 0) {
      setNodes(prevNodes => 
        prevNodes.map(node => {
          const status = nodeStatus[node.id];
          if (status) {
            return {
              ...node,
              data: {
                ...node.data,
                executionStatus: status.status,
                executionMessage: status.message,
                executionError: status.error,
              },
            };
          }
          return node;
        })
      );
    }
  }, [nodeStatus]);

  useEffect(() => {
    fetchProject();
  }, [id, get]);

  const deleteEdge = (edgeId: string) => {
    setEdges((eds) => eds.filter((e: any) => e.id !== edgeId));
  };

  const fetchProject = async () => {
    if (!id) return;
    if (id === 'new_workflow') {
        const startNode: Node = {
          id: 'node_start',
          type: 'customNode',
          position: { x: 250, y: 150 },
          data: { label: 'Start Event', piece: 'manual', config: {} },
        };
      setProject({ id: 'new_workflow', name: 'Process Comp [New]', nodes: [startNode], edges: [] });
      setNodes([startNode]);
      setEdges([]);
      setNodeCounter(1);
      setLoading(false);
      return;
    }
    try {
      const data: any = await get(`/api/workflows/${id}`);
      // Backend returns { success: true, workflow: { id, name, steps } }
      if (data.success && data.workflow) {
        const wf = data.workflow;
        setProject({ id: wf.id, name: wf.name, nodes: [], edges: [] });
        
        // Parse canvas_data (which holds nodes and edges) if it exists
        let canvasData: any = null;
        if (wf.steps && typeof wf.steps === 'string') {
          try { canvasData = JSON.parse(wf.steps); } catch (e) {}
        } else if (wf.steps && typeof wf.steps === 'object') {
          canvasData = wf.steps;
        }
        
        if (canvasData && canvasData.nodes) {
          setNodes(canvasData.nodes);
          const loadedEdges = (canvasData.edges || []).map((e: any) => ({
            ...e,
            type: 'buttonedge',
            data: { ...e.data, onDelete: deleteEdge }
          }));
          setEdges(loadedEdges);
          setVariables(canvasData.variables || []);
          if (canvasData.viewport) {
             setInitialViewport(canvasData.viewport);
          }
        } else {
          setNodes([]);
          setEdges([]);
          setVariables([]);
        }
      }
    } catch (err) {
      console.error('Failed to load project:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string) => {
    return {
      Triggers: '#8b5cf6',
      Connectors: '#22c55e',
      Logic: '#f59e0b',
    }[category] ?? '#475569';
  };

  const createNode = (piece: Piece, position: { x: number; y: number }) => {
    const newNodeId = `${piece.name}-${nodeCounter}`;
    setNodeCounter((count) => count + 1);
      const newNode: Node = {
        id: newNodeId,
        type: 'customNode',
        data: { label: piece.displayName, piece: piece.name, config: {}, icon: piece.icon },
        position,
        };
    setNodes((nds) => [...nds, newNode]);
  };

  const addNode = (piece: Piece) => {
    createNode(piece, { x: Math.random() * 420 + 60, y: Math.random() * 240 + 60 });
  };

  const onDragStart = (event: DragEvent<HTMLButtonElement>, piece: Piece) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(piece));
    event.dataTransfer.effectAllowed = 'move';
  };

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (!wrapperRef.current || !reactFlowInstance) return;
    const reactFlowBounds = wrapperRef.current.getBoundingClientRect();
    const data = event.dataTransfer.getData('application/reactflow');
    if (!data) return;
    const piece: Piece = JSON.parse(data);
    const position = reactFlowInstance.screenToFlowPosition({
      x: event.clientX,
      y: event.clientY,
    });
    createNode(piece, position);
  };

  const onConnect = (connection: Connection) => {
    setEdges((eds) => addEdge({ 
      ...connection, 
      type: 'buttonedge', 
      data: { onDelete: deleteEdge } 
    }, eds));
  };

  const onReconnect = useCallback((oldEdge: Edge, newConnection: Connection) => {
    setEdges((els) => reconnectEdge(oldEdge, newConnection, els));
  }, [setEdges]);

  useEffect(() => {
    if (reactFlowInstance && initialViewport) {
      reactFlowInstance.setViewport(initialViewport);
      setInitialViewport(null);
    }
  }, [reactFlowInstance, initialViewport]);

  const deleteNode = (nodeId: string) => {
    setNodes((nds) => nds.filter((n: any) => n.id !== nodeId));
    setEdges((eds) => eds.filter((e: any) => e.source !== nodeId && e.target !== nodeId));
    if (selectedNode === nodeId) setSelectedNode(null);
  };

  
  const handleSaveWorkflow = async () => {
    try {
      const payload = {
        agent_id: agentId,
        project_id: projectId ? Number(projectId) : null,
        name: project?.name || 'Untitled Workflow',
        steps: { nodes, edges, variables, viewport: reactFlowInstance?.getViewport() },
        status: 'active'
      };
      
      let res;
      if (id === 'new_workflow' || isNaN(Number(id))) {
        res = await post('/api/workflows', payload);
        if (res.workflow_id) {
            window.history.replaceState({}, '', `/v2-canvas?id=${res.workflow_id}`);
            setId(res.workflow_id.toString());
        }
      } else {
        res = await put(`/api/workflows/${id}`, payload);
      }
      
      alert('Workflow saved successfully!');
    } catch (e: any) {
      alert('Error saving workflow: ' + e.message);
    }
  };



  const handleExecuteWorkflow = async () => {
    if (!project) return;
    
    let currentId = id;
    if (currentId === 'new_workflow' || isNaN(Number(currentId))) {
      alert("Please save the workflow first before running.");
      return;
    }
    
    if (executionState.isExecuting) {
      alert('Workflow is already executing!');
      return;
    }
    
    try {
      // Clear previous execution state
      setExecutionLogs([]);
      setNodeStatus({});
          setEdgeExecutionCounts({});
          setActiveEdges({});
      
      setShowDebugPanel(true);
        const data = await post(`/api/workflows/${currentId}/execute`, { nodes, edges, variables });
      
      if (data.task_id) {
        setExecutionState(prev => ({
          ...prev,
          isExecuting: true,
          taskId: data.task_id,
        }));
      }
    } catch (err) {
      console.error('Failed to execute workflow:', err);
      alert(err instanceof Error ? err.message : 'Failed to execute workflow');
      setExecutionState(prev => ({
        ...prev,
        isExecuting: false,
      }));
    }
  };

  const handleStopWorkflow = async () => {
    try {
        await post(`/api/workflows/${id}/stop/${executionState.taskId || 'all'}`, {});
    } catch (err) {
        console.error('Failed to stop workflow:', err);
    }
    setExecutionState({
      isExecuting: false,
      currentNodeId: undefined,
      taskId: undefined,
    });
    setNodeStatus({});
          setEdgeExecutionCounts({});
          setActiveEdges({});
    setExecutionLogs([]);
  };

  const filteredPieces = workflowPieces.filter((piece) =>
    piece.displayName.toLowerCase().includes(searchPiece.toLowerCase()) ||
    piece.category.toLowerCase().includes(searchPiece.toLowerCase()) ||
    piece.description.toLowerCase().includes(searchPiece.toLowerCase()),
  );

  const groupedPieces = filteredPieces.reduce((acc, piece) => {
    acc[piece.category] = acc[piece.category] || [];
    acc[piece.category].push(piece);
    return acc;
  }, {} as Record<string, Piece[]>);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 text-slate-600">Loading project...</div>
    );
  }

  if (!project) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 text-red-400">Project not found</div>
    );
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-slate-50 text-slate-800 font-sans">
      {/* Top Header */}
      <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4 shrink-0 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <button onClick={navigateBack} className="p-1.5 text-slate-500 hover:bg-slate-100 rounded-md">
            <ArrowLeft size={18} />
          </button>
          <div className="flex items-center gap-2 w-64">

            <input
              type="text"
              value={project?.name || ''}
              onChange={(e) => setProject(prev => prev ? { ...prev, name: e.target.value } : null)}
              placeholder="Process Comp [New]"
              className="text-lg font-bold text-slate-800 bg-transparent border-none outline-none focus:ring-2 focus:ring-blue-100 rounded px-1 w-full"
            />
          </div>
        </div>
        
        <div className="flex items-center gap-2">
            <div className="w-px h-5 bg-slate-200 mx-1" />
            <button
              onClick={handleStopWorkflow}
              className={`flex items-center gap-1.5 px-4 py-1.5 text-sm font-semibold rounded-md transition-colors bg-red-50 text-red-600 hover:bg-red-100`}
            >
              <Square size={16} fill="currentColor" /> Stop
            </button>
            <button
              onClick={handleExecuteWorkflow}
              disabled={executionState.isExecuting || !nodes.length}
              className={`flex items-center gap-1.5 px-4 py-1.5 text-sm font-semibold rounded-md transition-colors ${
                executionState.isExecuting
                  ? 'bg-slate-50 text-slate-400'
                  : 'text-blue-600 hover:bg-blue-50'
              } ${(!nodes.length || executionState.isExecuting) ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {executionState.isExecuting ? (
                <><Loader2 size={16} className="animate-spin" /> Running...</>
              ) : (
                <><Play size={16} fill="currentColor" /> Run</>
              )}
            </button>
          <button
            onClick={handleSaveWorkflow}
            className="px-4 py-1.5 text-sm font-medium text-slate-700 border border-slate-300 rounded-md hover:bg-slate-50"
          >
            Save
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-[280px] border-r border-slate-200 bg-white flex flex-col overflow-hidden shrink-0">
          {/* Tabs */}
          <div className="flex border-b border-slate-200">
            <button
              onClick={() => setActiveLeftTab('variables')}
              className={`flex-1 py-2 text-sm font-medium border-b-2 ${activeLeftTab === 'variables' ? 'border-orange-500 text-slate-900' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
            >
              Variables
            </button>
            <button
              onClick={() => setActiveLeftTab('activities')}
              className={`flex-1 py-2 text-sm font-medium border-b-2 ${activeLeftTab === 'activities' ? 'border-orange-500 text-slate-900' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
            >
              Activities
            </button>
            <button
              onClick={() => setActiveLeftTab('triggers')}
              className={`flex-1 py-2 text-sm font-medium border-b-2 ${activeLeftTab === 'triggers' ? 'border-orange-500 text-slate-900' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
            >
              Triggers
            </button>
            <button
              onClick={() => setActiveLeftTab('runs')}
              className={`flex-1 py-2 text-sm font-medium border-b-2 ${activeLeftTab === 'runs' ? 'border-orange-500 text-slate-900' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
            >
              Runs
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 bg-slate-50">
            {activeLeftTab === 'activities' && (
              <div className="space-y-2">
                <div className="mb-4">
                  <input
                    type="text"
                    placeholder="Search elements"
                    value={searchPiece}
                    onChange={(e) => setSearchPiece(e.target.value)}
                    className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                  />
                </div>
                
                {Object.entries(groupedPieces)
                  .filter(([category]) => category !== 'Triggers')
                  .map(([category, pieces]) => (
                  <div key={category} className="mb-2">
                    <div className="flex items-center gap-2 w-full text-left py-1 text-sm font-semibold text-slate-700">
                      <ChevronDown size={14} />
                      {category}
                    </div>
                    
                    <div className="ml-5 mt-1 space-y-1">
                      {pieces.map((piece) => (
                        <div key={piece.name} className="flex flex-col gap-1">
                          <button
                            draggable
                            onDragStart={(e) => {
                              e.dataTransfer.setData('application/reactflow', JSON.stringify({
                                name: piece.name,
                                displayName: piece.displayName,
                                category: piece.category,
                                description: piece.description,
                              }));
                              e.dataTransfer.effectAllowed = 'move';
                            }}
                            className="flex items-center gap-2 px-2 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded cursor-grab active:cursor-grabbing w-full text-left"
                          >
                            <div className="w-6 h-6 flex items-center justify-center shrink-0">
                              {renderIcon(piece)}
                            </div>
                            <span className="truncate">{piece.displayName}</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            
            {activeLeftTab === 'variables' && (
              <div className="space-y-4">
                <div className="bg-white p-3 rounded-md border border-slate-200 shadow-sm">
                  <h3 className="text-xs font-bold text-slate-700 mb-2">Create Variable</h3>
                  <div className="space-y-2">
                    <input type="text" placeholder="Name" value={newVar.name} onChange={e => setNewVar({...newVar, name: e.target.value})} className="w-full text-xs p-1.5 border rounded" />
                    <div className="flex gap-2">
                      <select value={newVar.type} onChange={e => setNewVar({...newVar, type: e.target.value})} className="w-1/2 text-xs p-1.5 border rounded bg-white">
                        <option value="String">String</option>
                        <option value="Number">Number</option>
                        <option value="Boolean">Boolean</option>
                        <option value="Table">Table</option>
                        <option value="List">List</option>
                        <option value="Dictionary">Dictionary</option>
                      </select>
                      <select value={newVar.scope} onChange={e => setNewVar({...newVar, scope: e.target.value})} className="w-1/2 text-xs p-1.5 border rounded bg-white">
                        <option value="Input">Input</option>
                        <option value="Output">Output</option>
                      </select>
                    </div>
                    {['Table', 'List', 'Dictionary'].includes(newVar.type) ? (
                      <textarea placeholder='Default Value (JSON e.g. {"key": "value"})' value={newVar.value} onChange={e => setNewVar({...newVar, value: e.target.value})} className="w-full text-xs p-1.5 border rounded font-mono" rows={3} />
                    ) : (
                      <input type="text" placeholder="Default Value" value={newVar.value} onChange={e => setNewVar({...newVar, value: e.target.value})} className="w-full text-xs p-1.5 border rounded" />
                    )}
                    <button onClick={() => {
                      if (!newVar.name) return;
                      setVariables([...variables, { id: Math.random().toString(36).substr(2, 9), ...newVar }]);
                      setNewVar({name: '', type: 'String', scope: 'Input', value: ''});
                    }} className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs py-1.5 rounded font-medium">
                      Add Variable
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-slate-700">Existing Variables</h3>
                  {variables.length === 0 ? (
                    <div className="text-xs text-slate-500 italic text-center py-4">No variables created</div>
                  ) : (
                    variables.map(v => (
                      <div key={v.id} className="bg-white p-2 rounded-md border border-slate-200 flex flex-col gap-1 relative group">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-slate-800">{v.name}</span>
                          <button onClick={() => setVariables(variables.filter(x => x.id !== v.id))} className="text-red-500 opacity-0 group-hover:opacity-100"><Trash2 size={12}/></button>
                        </div>
                        <div className="flex gap-2 text-[10px] text-slate-500">
                          <span className="bg-slate-100 px-1.5 py-0.5 rounded">{v.type}</span>
                          <span className="bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded">{v.scope}</span>
                        </div>
                        {v.value && <div className="text-[10px] text-slate-500 truncate font-mono bg-slate-50 p-1 rounded mt-1">{v.value}</div>}
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            
            {activeLeftTab === 'triggers' && (
              <div className="space-y-2">
                {workflowPieces.filter(p => p.category === 'Triggers').map((piece) => (
                  <button
                    key={piece.name}
                    draggable
                    onDragStart={(e) => onDragStart(e, piece)}
                    className="flex items-center gap-2 px-2 py-1.5 text-sm text-slate-600 hover:bg-emerald-50 rounded cursor-grab active:cursor-grabbing w-full text-left"
                  >
                    <div className="w-6 h-6 flex items-center justify-center shrink-0">
                              {renderIcon(piece)}
                            </div>
                    <span className="truncate">{piece.displayName}</span>
                  </button>
                ))}
              </div>
            )}
            
            {activeLeftTab === 'runs' && (
              <div className="h-full">
                {id && id !== 'new_workflow' ? (
                  <ExecutionHistory workflowId={id} />
                ) : (
                  <div className="text-center text-slate-500 text-sm py-4">Save the workflow first to view its execution history.</div>
                )}
              </div>
            )}
          </div>
        </aside>

        {/* Canvas Area */}
        <div ref={wrapperRef} className="flex-1 bg-slate-50 relative" onDrop={onDrop} onDragOver={onDragOver}>
          <ReactFlow
            nodes={nodes}
            edges={styledEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onReconnect={onReconnect}
            onInit={(instance) => setReactFlowInstance(instance)}
            onNodeClick={(_, node) => setSelectedNode(node.id)}
            fitView
            style={{ width: '100%', height: '100%' }}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            defaultEdgeOptions={{ type: 'buttonedge', style: { strokeWidth: 2, stroke: '#94a3b8' } }}
          >
            <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#cbd5e1" />
            <Controls showInteractive={false} />
            <MiniMap />
          </ReactFlow>
          
          <DebugPanel
            isOpen={showDebugPanel}
            onClose={() => setShowDebugPanel(false)}
            executionState={executionState}
            logs={executionLogs}
            nodeStatus={nodeStatus}
          />
        </div>

        {/* Right Sidebar (Config) */}
        <aside className="w-[340px] border-l border-slate-200 bg-white p-5 overflow-y-auto shrink-0 flex flex-col">
          {selectedNode ? (
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-sm font-semibold text-slate-900">Event: {nodes.find((n: any) => n.id === selectedNode)?.data?.label}</h2>
                  <button onClick={() => selectedNode && deleteNode(selectedNode)} className="text-slate-400 hover:text-red-500">
                    <Trash2 size={16} />
                  </button>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed mb-4">
                  Configure the selected element. Required fields are highlighted in red.
                </p>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                      <AlertCircle size={12} className="text-red-500" /> Request title
                    </label>
                    <input
                      value={nodes.find((n: any) => n.id === selectedNode)?.data?.label ?? ''}
                      onChange={(e) => {
                        const value = e.target.value;
                        setNodes((nds) =>
                          nds.map((n: any) =>
                            n.id === selectedNode ? { ...n, data: { ...n.data, label: value } } : n,
                          ),
                        );
                      }}
                      placeholder="Required"
                      className="w-full border border-red-300 rounded px-3 py-1.5 text-sm focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1 flex justify-between">
                      <span>Node Variable ID</span>
                      <span className="text-slate-400 font-normal">Use this ID when typing variables</span>
                    </label>
                    <div className="flex gap-2">
                      <input
                        disabled
                        value={selectedNode ?? ''}
                        className="w-full border border-blue-200 bg-blue-50/50 rounded px-3 py-1.5 text-sm text-blue-600 font-mono font-medium"
                      />
                      <button
                        onClick={() => {
                          if (selectedNode) {
                            navigator.clipboard.writeText(`{{${selectedNode}}}`);
                            alert('Copied variable to clipboard!');
                          }
                        }}
                        className="px-3 py-1.5 bg-blue-100 text-blue-600 rounded text-xs font-semibold hover:bg-blue-200 transition-colors shrink-0"
                      >
                        Copy
                      </button>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Connector
                    </label>
                    <input
                      disabled
                      value={nodes.find((n: any) => n.id === selectedNode)?.data?.piece ?? ''}
                      className="w-full border border-slate-200 bg-slate-50 rounded px-3 py-1.5 text-sm text-slate-500"
                    />
                  </div>

                  <NodeConfigForm
                    pieceName={nodes.find((n: any) => n.id === selectedNode)?.data?.piece || ''}
                    config={nodes.find((n: any) => n.id === selectedNode)?.data?.config || {}}
                    variables={[
                      ...variables,
                      ...nodes.filter((n: any) => n.id !== selectedNode).map((n: any) => ({ name: `${n.id}_output` }))
                    ]}
                    projectId={projectId}
                    onConfigChange={(newConfig) => {
                      setNodes((nds) =>
                        nds.map((n: any) =>
                          n.id === selectedNode ? { ...n, data: { ...n.data, config: newConfig } } : n,
                        )
                      );
                    }}
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <AlertCircle size={32} className="mb-2 opacity-50" />
              <p className="text-sm font-medium">No Element Selected</p>
              <p className="text-xs text-center mt-1 max-w-[200px]">Click an element on the canvas to view and edit its properties.</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
