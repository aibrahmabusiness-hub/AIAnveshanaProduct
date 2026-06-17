import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Download, MoreVertical, Play, Edit2, Trash2, FileJson, Search, Filter } from 'lucide-react';
import useApi from '../hooks/useApi';

interface Workflow {
  id: number;
  name: string;
  status: string;
  created_at: string;
  steps: any;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { get, post, put, del } = useApi();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Run Modal State
  const [showRunModal, setShowRunModal] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [variableValues, setVariableValues] = useState<Record<string, string>>({});
  const [isRunning, setIsRunning] = useState(false);
  
  // Menu State
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);

  useEffect(() => {
    fetchWorkflows();
  }, [get]);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await get('/api/workflows');
      if (data.success) {
        setWorkflows(data.workflows || []);
      }
    } catch (err) {
      console.error('Failed to load workflows', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this workflow?')) return;
    try {
      await del(`/api/workflows/${id}`);
      setWorkflows(workflows.filter(w => w.id !== id));
      setOpenMenuId(null);
    } catch (err) {
      alert('Failed to delete workflow');
    }
  };

  const openRunModal = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    setOpenMenuId(null);
    
    // Initialize variables
    const vars = workflow.steps?.variables || [];
    const initialValues: Record<string, string> = {};
    vars.forEach((v: any) => {
      initialValues[v.name] = v.value || '';
    });
    setVariableValues(initialValues);
    setShowRunModal(true);
  };

  const handleToggleStatus = async (workflow: Workflow) => {
    const newStatus = workflow.status === 'active' ? 'inactive' : 'active';
    // Optimistic UI update
    setWorkflows(workflows.map(w => w.id === workflow.id ? { ...w, status: newStatus } : w));
    try {
      await put(`/api/workflows/${workflow.id}/status`, { status: newStatus });
    } catch (err) {
      alert('Failed to update status');
      // Revert on failure
      setWorkflows(workflows.map(w => w.id === workflow.id ? { ...w, status: workflow.status } : w));
    }
  };

  const handleRunWorkflow = async () => {
    if (!selectedWorkflow) return;
    setIsRunning(true);
    try {
      // Reconstruct payload with updated variables
      const payload = {
        nodes: selectedWorkflow.steps?.nodes || [],
        edges: selectedWorkflow.steps?.edges || [],
        variables: Object.keys(variableValues).map(name => ({
          name,
          value: variableValues[name]
        }))
      };

      const res = await post(`/api/workflows/${selectedWorkflow.id}/execute`, payload);
      if (res.task_id) {
        alert('Workflow dispatched successfully!');
      } else {
        alert('Failed to dispatch workflow');
      }
      setShowRunModal(false);
    } catch (err: any) {
      alert('Error running workflow: ' + err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const formatRelativeTime = (dateStr: string) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    const now = new Date();
    const diffHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffHours < 24) {
      return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } else if (diffHours < 48) {
      return `Yesterday at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    }
    return date.toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-[#f9fafb] text-slate-800 font-sans">
      <div className="mx-auto max-w-[1200px] p-8 pt-12">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Flows</h1>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition-colors shadow-sm">
              <Download size={16} /> Import Flow
            </button>
            <button 
              onClick={() => navigate('/v2-canvas?id=new_workflow')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-[#ff6d29] border border-transparent rounded-md hover:bg-[#e85b1c] transition-colors shadow-sm"
            >
              New Flow <span className="ml-1 text-white/70">v</span>
            </button>
          </div>
        </header>

        {/* Filters */}
        <div className="flex gap-3 mb-6">
          <button className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-full shadow-sm hover:bg-slate-50 transition-colors">
            <Plus size={14} className="text-slate-400" /> Flow name
          </button>
          <button className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-full shadow-sm hover:bg-slate-50 transition-colors">
            <Plus size={14} className="text-slate-400" /> Status
          </button>
        </div>

        {/* Table Container */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-visible relative">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="py-4 px-6 text-xs font-semibold text-slate-700 w-1/3">Name</th>
                <th className="py-4 px-6 text-xs font-semibold text-slate-700">Steps</th>
                <th className="py-4 px-6 text-xs font-semibold text-slate-700">Created</th>
                <th className="py-4 px-6 text-xs font-semibold text-slate-700">Status</th>
                <th className="py-4 px-6 w-16"></th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500 text-sm">Loading flows...</td>
                </tr>
              ) : workflows.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500 text-sm">No flows found.</td>
                </tr>
              ) : (
                workflows.map((workflow) => {
                  const nodeCount = workflow.steps?.nodes?.length || 0;
                  
                  return (
                    <tr key={workflow.id} className="border-b border-slate-50 last:border-0 hover:bg-slate-50/50 group transition-colors">
                      <td className="py-4 px-6">
                        <button 
                          onClick={() => navigate(`/v2-canvas?id=${workflow.id}`)}
                          className="text-sm text-slate-600 font-medium hover:text-slate-900"
                        >
                          {workflow.name || 'Untitled'}
                        </button>
                      </td>
                      <td className="py-4 px-6">
                        {nodeCount > 0 ? (
                          <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center border border-slate-100">
                            <FileJson size={14} className="text-slate-400" />
                          </div>
                        ) : (
                          <span className="text-slate-400 text-sm">-</span>
                        )}
                      </td>
                      <td className="py-4 px-6 text-sm text-slate-500 font-medium">
                        {formatRelativeTime(workflow.created_at)}
                      </td>
                      <td className="py-4 px-6">
                        {/* Toggle Switch styling */}
                        <div 
                          onClick={() => handleToggleStatus(workflow)}
                          className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${workflow.status === 'active' ? 'bg-[#22c55e]' : 'bg-slate-200'}`}>
                          <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-all ${workflow.status === 'active' ? 'left-[22px]' : 'left-0.5'}`}></div>
                        </div>
                      </td>
                      <td className="py-4 px-6 relative">
                        <button 
                          onClick={() => setOpenMenuId(openMenuId === workflow.id ? null : workflow.id)}
                          className="p-1.5 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-100 opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100"
                        >
                          <MoreVertical size={18} />
                        </button>
                        
                        {/* Dropdown Menu */}
                        {openMenuId === workflow.id && (
                          <div className="absolute right-8 top-10 w-40 bg-white rounded-md shadow-lg border border-slate-200 py-1 z-10">
                            <button 
                              onClick={() => navigate(`/v2-canvas?id=${workflow.id}`)}
                              className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 flex items-center gap-2"
                            >
                              <Edit2 size={14} /> Edit
                            </button>
                            <button 
                              onClick={() => openRunModal(workflow)}
                              className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 flex items-center gap-2"
                            >
                              <Play size={14} /> Run
                            </button>
                            <div className="h-px bg-slate-100 my-1"></div>
                            <button 
                              onClick={() => handleDelete(workflow.id)}
                              className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                            >
                              <Trash2 size={14} /> Delete
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
          
          {/* Pagination Footer */}
          <div className="flex justify-end items-center px-6 py-4 border-t border-slate-100 gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-500">Rows per page</span>
              <select className="border border-slate-200 rounded-md text-sm px-2 py-1 text-slate-600 bg-white shadow-sm outline-none">
                <option>10</option>
                <option>20</option>
                <option>50</option>
              </select>
            </div>
            <div className="flex gap-2">
              <button className="px-3 py-1 text-sm text-slate-400 bg-white border border-slate-200 rounded-md cursor-not-allowed">
                Previous
              </button>
              <button className="px-3 py-1 text-sm text-slate-600 bg-white border border-slate-200 rounded-md hover:bg-slate-50 shadow-sm transition-colors">
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Run Workflow Modal */}
      {showRunModal && selectedWorkflow && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl overflow-hidden border border-slate-200">
            <div className="px-6 py-4 border-b border-slate-100">
              <h2 className="text-xl font-bold text-slate-800">Run: {selectedWorkflow.name}</h2>
              <p className="text-sm text-slate-500 mt-1">Provide values for your workflow variables before execution.</p>
            </div>
            
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              {Object.keys(variableValues).length === 0 ? (
                <div className="text-center py-6 text-slate-500 text-sm">
                  This workflow doesn't require any input variables. Click Run to start execution immediately.
                </div>
              ) : (
                <div className="space-y-4">
                  {Object.keys(variableValues).map((varName) => (
                    <div key={varName}>
                      <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                        {varName}
                      </label>
                      <input
                        type="text"
                        value={variableValues[varName]}
                        onChange={(e) => setVariableValues({...variableValues, [varName]: e.target.value})}
                        placeholder={`Enter value for ${varName}`}
                        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-800 focus:border-[#ff6d29] focus:ring-1 focus:ring-[#ff6d29] outline-none transition-shadow"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
              <button
                onClick={() => setShowRunModal(false)}
                className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
                disabled={isRunning}
              >
                Cancel
              </button>
              <button
                onClick={handleRunWorkflow}
                disabled={isRunning}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-[#ff6d29] rounded-md hover:bg-[#e85b1c] transition-colors shadow-sm disabled:opacity-50"
              >
                {isRunning ? (
                  <>Running...</>
                ) : (
                  <><Play size={14} /> Run Workflow</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
