import React from 'react';
import { X, Play, CheckCircle, XCircle, Clock, Loader2, AlertCircle } from 'lucide-react';
import { NodeExecutionStatus, WorkflowExecutionState } from '../types/flowTypes';

interface DebugPanelProps {
  isOpen: boolean;
  onClose: () => void;
  executionState: WorkflowExecutionState;
  logs: {
    message: string;
    timestamp: string;
    type: 'info' | 'success' | 'error';
    nodeId?: string;
    inputs?: any;
    result?: any;
    duration?: number;
  }[];
  nodeStatus: NodeExecutionStatus;
}

export default function DebugPanel({ isOpen, onClose, executionState, logs, nodeStatus }: DebugPanelProps) {
  if (!isOpen) return null;

  return (
    <div className="absolute bottom-0 left-0 right-0 h-[300px] bg-white border-t border-slate-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-50 flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-200 bg-slate-50 shrink-0">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
            Execution Result
            {executionState.isExecuting && (
              <span className="flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded bg-blue-100 text-blue-700">
                <Loader2 size={12} className="animate-spin" /> In Progress
              </span>
            )}
          </h3>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-200 rounded text-slate-500 transition-colors">
          <X size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4 bg-[#1e293b] text-slate-300 font-mono text-xs">
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-2">
            <Clock size={24} />
            <span>Waiting for execution logs...</span>
          </div>
        ) : (
          <div className="space-y-2">
            {logs.map((log, idx) => (
              <div key={idx} className={`p-2 rounded ${
                log.type === 'error' ? 'bg-red-950/50 text-red-400' :
                log.type === 'success' ? 'bg-emerald-950/50 text-emerald-400' :
                'bg-slate-800/50 text-slate-300'
              }`}>
                <div className="flex items-start gap-2">
                  <div className="mt-0.5 shrink-0">
                    {log.type === 'error' ? <XCircle size={14} /> :
                     log.type === 'success' ? <CheckCircle size={14} /> :
                     <AlertCircle size={14} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-semibold">[{new Date(log.timestamp).toLocaleTimeString()}] {log.message}</span>
                      {log.duration && <span className="text-slate-500">{log.duration}ms</span>}
                    </div>
                    {log.inputs && Object.keys(log.inputs).length > 0 && (
                      <div className="mt-1 pl-2 border-l-2 border-slate-700">
                        <span className="text-slate-500 block mb-0.5">Inputs:</span>
                        <pre className="whitespace-pre-wrap break-words">{JSON.stringify(log.inputs, null, 2)}</pre>
                      </div>
                    )}
                    {log.result && (
                      <div className="mt-1 pl-2 border-l-2 border-emerald-900">
                        <span className="text-slate-500 block mb-0.5">Result:</span>
                        <pre className="whitespace-pre-wrap break-words text-emerald-200">{JSON.stringify(log.result, null, 2)}</pre>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
