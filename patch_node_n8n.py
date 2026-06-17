import re

filepath_node = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\nodes\BaseNode.tsx'
with open(filepath_node, 'r', encoding='utf-8') as f:
    content = f.read()

old_render = """function BaseNode({ data, isConnectable, type }: NodeProps) {
  const nodeData = data as NodeData;
  const nodeType: string = nodeData.piece || type || 'unknown';
  
  const isTrigger = nodeType.startsWith('trigger') || ['manual', 'webhook', 'schedule'].includes(nodeType);
  const executionStatus: string | undefined = nodeData.executionStatus;
  const statusMessage: string | undefined = nodeData.executionMessage;
  const statusError: string | undefined = nodeData.executionError;
  const categoryColor = getCategoryColor(nodeData.category as string);

  return (
    <div className={`
      w-[220px] bg-white text-slate-800 rounded-xl shadow-md overflow-hidden relative
      transition-all duration-200 hover:shadow-lg
      ${getStatusBorder(executionStatus)}
    `}>
      {/* Top colored border bar like n8n */}
      <div className="h-1.5 w-full" style={{ backgroundColor: categoryColor }} />
      
      {/* Target Handle (Input) - Not for triggers */}
      {!isTrigger && (
        <Handle
          type="target"
          position={Position.Left}
          isConnectable={isConnectable}
          className="w-3 h-3 bg-slate-400 border-2 border-white -ml-1"
        />
      )}

      {/* Node Content */}
      <div className="p-3 flex items-center justify-between">
        <div className="flex items-center space-x-3 w-full">
          <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-slate-50 rounded-lg border border-slate-100">
            {getPieceLogo(nodeType)}
          </div>
          <div className="overflow-hidden flex-1">
            <h3 className="text-[13px] font-bold truncate tracking-tight text-slate-800">{nodeData.label || nodeType}</h3>
            <p className="text-[10px] text-slate-500 truncate capitalize font-medium">{nodeType.replace(/_/g, ' ')}</p>
          </div>
        </div>
        
        {/* Status indicator */}
        {executionStatus && (
          <div className="flex items-center gap-1 flex-shrink-0 ml-2">
            {getStatusIcon(executionStatus)}
          </div>
        )}
      </div>

      {/* Status message */}
      {executionStatus && (
        <div className="px-3 pb-3">
          <div className={`
            text-[10px] font-mono px-2 py-1 rounded border
            ${executionStatus === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' :
              executionStatus === 'error' ? 'bg-red-50 border-red-200 text-red-700' :
              'bg-blue-50 border-blue-200 text-blue-700'}
          `}>
            {statusMessage || statusError || executionStatus}
          </div>
        </div>
      )}

      {/* Source Handle (Output) */}
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-slate-400 border-2 border-white -mr-1"
      />
    </div>
  );
}"""

new_render = """function BaseNode({ data, isConnectable, type }: NodeProps) {
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
          relative w-[72px] h-[72px] bg-white border-2 flex items-center justify-center shadow-sm
          transition-all duration-200 hover:shadow-md
          ${isTrigger ? 'rounded-l-[36px] rounded-r-xl' : 'rounded-xl'}
          ${executionStatus ? getStatusBorder(executionStatus) : ''}
        `}
        style={{ borderColor: executionStatus ? undefined : categoryColor }}
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
          {getPieceLogo(nodeType)}
        </div>

        {/* Status indicator badge (top right) */}
        {executionStatus && (
          <div className="absolute -top-2 -right-2 bg-white rounded-full shadow-sm p-0.5 z-10">
            {getStatusIcon(executionStatus)}
          </div>
        )}

        {/* Source Handle (Output) */}
        <Handle
          type="source"
          position={Position.Right}
          isConnectable={isConnectable}
          className="w-2.5 h-2.5 bg-slate-400 border-white"
        />
      </div>

      {/* Text Label Below */}
      <div className="mt-3 text-center w-full px-1">
        <h3 className="text-[13px] font-bold text-slate-800 leading-tight">
          {nodeData.label || nodeType}
        </h3>
        <p className="text-[10px] text-slate-500 mt-1 capitalize font-medium">
          {nodeData.action ? nodeData.action.replace(/_/g, ' ') : nodeType.replace(/_/g, ' ')}
        </p>
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
}"""
content = content.replace(old_render, new_render)

# Fix execution status icons to match n8n's solid badge style
old_icons = """// Execution status icon
const getStatusIcon = (status: string | undefined) => {
  switch (status) {
    case 'running':
      return <Loader2 className="w-3 h-3 animate-spin text-blue-400" />;
    case 'success':
      return <CheckCircle className="w-3 h-3 text-emerald-400" />;
    case 'error':
      return <XCircle className="w-3 h-3 text-red-400" />;
    default:
      return null;
  }
};"""

new_icons = """// Execution status icon
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
};"""
content = content.replace(old_icons, new_icons)

# Fix execution status borders
old_borders = """// Execution status colors
const getStatusBorder = (status: string | undefined) => {
  switch (status) {
    case 'running':
      return 'border-blue-400 shadow-blue-400/20 animate-pulse';
    case 'success':
      return 'border-emerald-500 shadow-emerald-500/20';
    case 'error':
      return 'border-red-500 shadow-red-500/20';
    default:
      return 'border-slate-200';
  }
};"""

new_borders = """// Execution status colors
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
};"""
content = content.replace(old_borders, new_borders)

with open(filepath_node, 'w', encoding='utf-8') as f:
    f.write(content)
