import { useState, useEffect } from 'react';
import { Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import useApi from '../hooks/useApi';

interface ExecutionRecord {
  id: string;
  workflow_id: string;
  name: string;
  task_id: string;
  status: 'completed' | 'failed' | 'pending';
  results: Record<string, any>;
  started_at: string;
  finished_at: string;
}

interface ExecutionHistoryProps {
  workflowId: string;
}

export default function ExecutionHistory({ workflowId }: ExecutionHistoryProps) {
  const { get } = useApi();
  const [history, setHistory] = useState<ExecutionRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchHistory = async () => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      let projectId = urlParams.get('project_id') || '';
      if (!projectId) {
        try {
          if (window.parent && window.parent.location.pathname.includes('/project/')) {
            projectId = window.parent.location.pathname.split('/').filter(Boolean).pop() || '';
          }
        } catch (e) {}
      }
      
      const data = await get(`/api/workflows/runs?project_id=${projectId || 0}&workflow_id=${workflowId}`);
      setHistory(data && data.runs && Array.isArray(data.runs) ? data.runs : []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="text-green-600" />;
      case 'failed':
        return <XCircle size={16} className="text-red-600" />;
      case 'pending':
        return <AlertCircle size={16} className="text-yellow-600" />;
      default:
        return <Clock size={16} className="text-slate-400" />;
    }
  };

  if (loading) {
    return <div className="text-slate-600 text-sm">Loading history...</div>;
  }

  return (
    <div className="space-y-2">
      <h4 className="font-semibold text-slate-900 text-sm">Execution History</h4>
      {history.length === 0 ? (
        <p className="text-xs text-slate-600">No executions yet</p>
      ) : (
        <div className="space-y-2">
          {history.map((record) => (
            <div
              key={record.id}
              className="flex items-center gap-2 p-2 bg-white border border-slate-200 rounded-lg"
            >
              {getStatusIcon(record.status)}
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-slate-900 truncate">
                  {record.name}
                </p>
                <p className="text-xs text-slate-600">
                  {new Date(record.started_at).toLocaleTimeString()}
                </p>
              </div>
              <span
                className={`text-xs font-semibold px-2 py-1 rounded ${
                  record.status === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : record.status === 'failed'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {record.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
