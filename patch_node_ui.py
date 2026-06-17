import re

# 1. Patch Project.tsx to remove the huge padding in createNode
filepath_project = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx'
with open(filepath_project, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the style object inside createNode
old_create_node_style = """      const newNode: Node = {
        id: newNodeId,
        type: 'default',
        data: { label: piece.displayName, piece: piece.name, config: {} },
        position,
        style: {
          background: getCategoryColor(piece.category),
          border: 'none',
          borderRadius: '18px',
          padding: '14px 18px',
          color: '#ffffff',
          fontWeight: 700,
          minWidth: 170,
        },
      };"""

new_create_node_style = """      const newNode: Node = {
        id: newNodeId,
        type: 'default',
        data: { label: piece.displayName, piece: piece.name, config: {}, category: piece.category },
        position,
      };"""
content = content.replace(old_create_node_style, new_create_node_style)

with open(filepath_project, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Patch BaseNode.tsx to use proper logos and sleek design
filepath_node = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\nodes\BaseNode.tsx'
with open(filepath_node, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace iconMap with a URL mapper
old_icon_map = """// Extended icon map for all piece types
const iconMap: Record<string, React.ComponentType<{ className?: string; size?: number }>> = {
  // Triggers
  manual: AlarmClock,
  trigger_manual: AlarmClock,
  webhook: Webhook,
  trigger_webhook: Webhook,
  schedule: Calendar,
  trigger_schedule: Calendar,
  
  // Email
  gmail: Mail,
  action_gmail: Mail,
  smtp: Mail,
  action_smtp: Mail,
  
  // Communication
  slack: MessageSquare,
  action_slack: MessageSquare,
  discord: MessageSquare,
  action_discord: MessageSquare,
  telegram: Send,
  action_telegram: Send,
  
  // Project Management
  jira: Briefcase,
  action_jira: Briefcase,
  asana: CheckCircle,
  action_asana: CheckCircle,
  monday: BarChart3,
  action_monday: BarChart3,
  
  // CRM
  salesforce: Users,
  action_salesforce: Users,
  hubspot: Users,
  action_hubspot: Users,
  
  // Database
  airtable: Database,
  action_airtable: Database,
  mongodb: Database,
  action_mongodb: Database,
  
  // Logic
  condition: GitBranch,
  logic_condition: GitBranch,
  loop: Repeat,
  logic_loop: Repeat,
  delay: Timer,
  logic_delay: Timer,
  
  // Default
  default: Settings,
};"""

new_icon_map = """// Map to CDN simpleicons or use lucide fallback
const getPieceLogo = (piece: string) => {
  const p = piece.replace('action_', '').replace('trigger_', '').replace('logic_', '');
  
  // Native icons
  if (['manual', 'schedule', 'delay', 'condition', 'loop'].includes(p)) {
    if (p === 'manual') return <AlarmClock className="w-5 h-5 text-slate-600" />;
    if (p === 'schedule') return <Calendar className="w-5 h-5 text-slate-600" />;
    if (p === 'delay') return <Timer className="w-5 h-5 text-slate-600" />;
    if (p === 'condition') return <GitBranch className="w-5 h-5 text-slate-600" />;
    if (p === 'loop') return <Repeat className="w-5 h-5 text-slate-600" />;
  }
  if (p === 'webhook') return <Webhook className="w-5 h-5 text-slate-600" />;
  
  // Custom simpleicons URL for others
  const cdnName = p === 'gmail' ? 'gmail' : p;
  return <img src={`https://cdn.simpleicons.org/${cdnName}`} alt={p} className="w-5 h-5 object-contain" onError={(e) => {
    (e.target as HTMLImageElement).src = 'https://cdn.simpleicons.org/appwrite'; // generic fallback
  }} />;
};

const getCategoryColor = (category?: string) => {
  return {
    'Triggers': '#a855f7',
    'Connectors': '#22c55e',
    'Logic': '#3b82f6',
  }[category || ''] ?? '#475569';
};
"""
content = content.replace(old_icon_map, new_icon_map)

# Replace the render structure
old_render = """function BaseNode({ data, isConnectable, type }: NodeProps) {
  const nodeData = data as NodeData;
  const nodeType: string = nodeData.piece || type || 'unknown';
  const Icon = iconMap[nodeType] || iconMap.default;
  
  const isTrigger = nodeType.startsWith('trigger') || ['manual', 'webhook', 'schedule'].includes(nodeType);
  const executionStatus: string | undefined = nodeData.executionStatus;
  const statusMessage: string | undefined = nodeData.executionMessage;
  const statusError: string | undefined = nodeData.executionError;

  return (
    <div className={`
      w-[180px] bg-white text-slate-800 rounded-lg border shadow-sm overflow-hidden
      transition-all duration-200 hover:shadow-md
      ${getStatusBorder(executionStatus)}
    `}>
      {/* Target Handle (Input) - Not for triggers */}
      {!isTrigger && (
        <Handle
          type="target"
          position={Position.Left}
          isConnectable={isConnectable}
          className="w-2.5 h-2.5 bg-slate-400 border-white"
        />
      )}

      {/* Node Header */}
      <div className={`
        px-3 py-2 flex items-center justify-between
        ${isTrigger ? 'bg-emerald-50/50' : 'bg-slate-50/50'}
      `}>
        <div className="flex items-center space-x-2">
          <div className={`
            p-1.5 rounded-md
            ${isTrigger ? 'bg-emerald-100 text-emerald-600' : 'bg-blue-100 text-blue-600'}
          `}>
            <Icon className="w-3.5 h-3.5" />
          </div>
          <div className="overflow-hidden">
            <h3 className="text-[11px] font-semibold truncate tracking-tight text-slate-700">{nodeData.label || nodeType}</h3>
            <p className="text-[9px] text-slate-500 truncate capitalize">{nodeType.replace('_', ' ').replace('action ', '').replace('trigger ', '')}</p>
          </div>
        </div>
        
        {/* Status indicator */}
        {executionStatus && (
          <div className="flex items-center gap-1">
            {getStatusIcon(executionStatus)}
          </div>
        )}
      </div>

        {/* Status message only */}
        {executionStatus && (
          <div className="px-3 pb-2">
          <div className={`
            text-[10px] px-1.5 py-0.5 rounded border
            ${executionStatus === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-600' :
              executionStatus === 'error' ? 'bg-red-50 border-red-200 text-red-600' :
              'bg-blue-50 border-blue-200 text-blue-600'}
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
        className="w-2.5 h-2.5 bg-blue-500 border-white"
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
content = content.replace(old_render, new_render)

with open(filepath_node, 'w', encoding='utf-8') as f:
    f.write(content)
