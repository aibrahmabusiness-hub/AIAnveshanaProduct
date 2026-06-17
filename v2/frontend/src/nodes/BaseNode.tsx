import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import {
  Settings, Mail, MessageSquare, Briefcase, AlarmClock, Webhook, Calendar,
  Code, Database, FileText, Users, BarChart3, Zap, CheckCircle, XCircle, AlertCircle,
  Loader2, GitBranch, Repeat, Timer, Send, Bell, ShoppingCart, CreditCard, Bot
} from 'lucide-react';

// Define the data type that our nodes will have
interface NodeData {
  label: string;
  piece?: string;
  config?: Record<string, any>;
  executionStatus?: 'idle' | 'running' | 'success' | 'error';
  executionMessage?: string;
  executionError?: string;
  icon?: string;
  [key: string]: unknown;
}

// Map to CDN simpleicons or use lucide fallback
const getPieceLogo = (piece: string, iconUrl?: string) => {
  if (iconUrl) {
    return <img src={iconUrl} alt={piece} className="w-5 h-5 object-contain" onError={(e) => {
      const target = e.target as HTMLImageElement;
      target.onerror = null;
      target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 8v8M8 12h8"/></svg>'; // generic fallback SVG
    }} />;
  }
  const p = piece.replace('action_', '').replace('trigger_', '').replace('logic_', '');
  
  // Native icons
  if (['manual', 'schedule', 'delay', 'condition', 'loop', 'ai_agent'].includes(p)) {
    if (p === 'manual') return <AlarmClock className="w-5 h-5 text-slate-600" />;
    if (p === 'schedule') return <Calendar className="w-5 h-5 text-slate-600" />;
    if (p === 'delay') return <Timer className="w-5 h-5 text-slate-600" />;
    if (p === 'condition') return <GitBranch className="w-5 h-5 text-slate-600" />;
    if (p === 'loop') return <Repeat className="w-5 h-5 text-slate-600" />;
    if (p === 'ai_agent') return <Bot className="w-5 h-5 text-purple-600" />;
  }
  if (p === 'webhook') return <Webhook className="w-5 h-5 text-slate-600" />;
  
  // Custom simpleicons URL for others
  const cdnName = p.split('_')[0]; // Extract the base app name (e.g. gmail_read_email -> gmail)
  return <img src={`https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/${cdnName}.svg`} alt={p} className="w-5 h-5 object-contain" onError={(e) => {
    const target = e.target as HTMLImageElement;
    target.onerror = null;
    target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 8v8M8 12h8"/></svg>'; // generic fallback SVG
  }} />;
};

const getCategoryColor = (category?: string) => {
  return {
    'Triggers': '#a855f7',
    'Connectors': '#22c55e',
    'Logic': '#3b82f6',
  }[category || ''] ?? '#475569';
};


// Execution status colors
const getStatusBorder = (status: string | undefined) => {
  switch (status) {
    case 'running':
      return 'border-blue-500 shadow-blue-500/30 shadow-md animate-pulse';
    case 'success':
      return 'border-emerald-500 shadow-emerald-500/30 shadow-md';
    case 'error':
      return 'border-red-500 shadow-red-500/30 shadow-md';
    default:
      return 'border-slate-200';
  }
};

// Execution status icon
const getStatusIcon = (status: string | undefined) => {
  switch (status) {
    case 'running':
      return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
    case 'success':
      return <CheckCircle className="w-4 h-4 text-emerald-500 fill-emerald-100" />;
    case 'error':
      return <AlertCircle className="w-4 h-4 text-red-500 fill-red-100" />;
    default:
      return null;
  }
};

function BaseNode({ id, data, isConnectable, type }: NodeProps) {
  const nodeData = data as NodeData;
  const nodeType: string = nodeData.piece || type || 'unknown';
  
  const isTrigger = nodeType.startsWith('trigger') || ['manual', 'webhook', 'schedule'].includes(nodeType);
  const executionStatus: string | undefined = nodeData.executionStatus;
  const statusMessage: string | undefined = nodeData.executionMessage;
  const statusError: string | undefined = nodeData.executionError;
  const categoryColor = getCategoryColor(nodeData.category as string);

  return (
    <div className="flex flex-col items-center w-[180px]">
      {/* Icon Box Container */}
      <div 
        className={`
          relative w-[72px] h-[72px] bg-white border border-slate-200 flex items-center justify-center shadow-sm
          transition-all duration-200 hover:shadow-md hover:border-slate-300
          ${isTrigger ? 'rounded-l-[36px] rounded-r-xl' : 'rounded-xl'}
          ${executionStatus ? getStatusBorder(executionStatus) : ''}
        `}
      >
        {/* Target Handle (Input) - Not for triggers */}
        {!isTrigger && (
          <Handle
            type="target"
            position={Position.Left}
            isConnectable={isConnectable}
            className="w-2.5 h-2.5 bg-slate-400 border-white"
          />
        )}

        {/* The Logo */}
        <div className="w-10 h-10 flex items-center justify-center">
          {getPieceLogo(nodeType, nodeData.icon as string)}
        </div>

        {/* Status indicator badge (top right) */}
        {executionStatus && (
          <div className="absolute -top-2 -right-2 bg-white rounded-full shadow-sm p-0.5 z-10">
            {getStatusIcon(executionStatus)}
          </div>
        )}

        {/* Source Handles (Outputs) */}
        {nodeType === 'logic_loop' ? (
          <div className="absolute -right-[5px] top-0 bottom-0 flex flex-col justify-evenly z-20">
            <div className="relative flex items-center justify-center">
              <span className="absolute -left-7 text-[9px] font-bold text-slate-500 whitespace-nowrap bg-white px-0.5 rounded shadow-sm z-10 border border-slate-100">loop</span>
              <Handle
                type="source"
                id="loop"
                position={Position.Right}
                isConnectable={isConnectable}
                className="!relative !transform-none !right-0 w-3 h-3 bg-slate-400 border-white hover:bg-blue-500 transition-colors"
              />
            </div>
            <div className="relative flex items-center justify-center">
              <span className="absolute -left-7 text-[9px] font-bold text-slate-500 whitespace-nowrap bg-white px-0.5 rounded shadow-sm z-10 border border-slate-100">done</span>
              <Handle
                type="source"
                id="done"
                position={Position.Right}
                isConnectable={isConnectable}
                className="!relative !transform-none !right-0 w-3 h-3 bg-slate-400 border-white hover:bg-emerald-500 transition-colors"
              />
            </div>
          </div>
        ) : nodeType === 'condition' ? (
          <div className="absolute -right-[5px] top-0 bottom-0 flex flex-col justify-evenly z-20">
            <div className="relative flex items-center justify-center">
              <span className="absolute -left-7 text-[9px] font-bold text-slate-500 whitespace-nowrap bg-white px-0.5 rounded shadow-sm z-10 border border-slate-100">true</span>
              <Handle
                type="source"
                id="true"
                position={Position.Right}
                isConnectable={isConnectable}
                className="!relative !transform-none !right-0 w-3 h-3 bg-slate-400 border-white hover:bg-emerald-500 transition-colors"
              />
            </div>
            <div className="relative flex items-center justify-center">
              <span className="absolute -left-8 text-[9px] font-bold text-slate-500 whitespace-nowrap bg-white px-0.5 rounded shadow-sm z-10 border border-slate-100">false</span>
              <Handle
                type="source"
                id="false"
                position={Position.Right}
                isConnectable={isConnectable}
                className="!relative !transform-none !right-0 w-3 h-3 bg-slate-400 border-white hover:bg-red-500 transition-colors"
              />
            </div>
          </div>
        ) : (
          <Handle
            type="source"
            position={Position.Right}
            isConnectable={isConnectable}
            className="w-2.5 h-2.5 bg-slate-400 border-white hover:bg-blue-500 transition-colors"
          />
        )}
      </div>

      {/* Text Label Below */}
      <div className="mt-3 text-center w-full px-1">
        <h3 className="text-[13px] font-bold text-slate-800 leading-tight">
          {nodeData.label || nodeType}
        </h3>
        <p className="text-[10px] text-slate-500 mt-1 capitalize font-medium">
          {nodeData.action ? (nodeData.action as string).replace(/_/g, ' ') : nodeType.replace(/_/g, ' ')}
        </p>
        <div className="mt-1.5 flex justify-center">
          <span className="px-1.5 py-0.5 bg-blue-50/80 border border-blue-200/60 rounded text-[9px] font-mono text-blue-600 truncate max-w-full inline-block cursor-copy" title="Copy Variable ID" onClick={() => { navigator.clipboard.writeText(`{{${id}}}`); alert('Copied ID to clipboard!'); }}>
            {id}
          </span>
        </div>
      </div>

      {/* Status message below text */}
      {executionStatus && (statusMessage || statusError) && (
        <div className={`
          mt-2 text-[10px] font-mono px-2 py-1 rounded border max-w-full truncate
          ${executionStatus === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' :
            executionStatus === 'error' ? 'bg-red-50 border-red-200 text-red-700' :
            'bg-blue-50 border-blue-200 text-blue-700'}
        `}>
          {statusMessage || statusError}
        </div>
      )}
    </div>
  );
}

export default memo(BaseNode);
