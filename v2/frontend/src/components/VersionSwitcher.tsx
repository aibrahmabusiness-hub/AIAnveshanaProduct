import React from 'react';
import { useWorkflowVersion } from '../contexts/WorkflowVersionContext';
import { ChevronDown } from 'lucide-react';

export default function VersionSwitcher() {
  const { version, versions, switchVersion } = useWorkflowVersion();
  const [isOpen, setIsOpen] = React.useState(false);

  const currentVersion = versions.find(v => v.id === version);

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'amber':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'cyan':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
      case 'emerald':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'rose':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    }
  };

  const getDotColor = (color: string, isActive: boolean) => {
    if (isActive) {
      return `bg-${color}-400`;
    }
    return `bg-${color}-600/30`;
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          inline-flex items-center gap-2 rounded-2xl px-4 py-2 text-sm font-medium
          border transition-all duration-200
          ${getColorClasses(currentVersion?.color || 'cyan')}
          hover:opacity-80
        `}
      >
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-current opacity-60"></span>
          {currentVersion?.name || version}
        </span>
        <ChevronDown
          size={14}
          className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-full mt-2 w-60 z-50 rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl shadow-slate-950/30 overflow-hidden">
            <div className="p-1">
              {versions.map((v) => {
                const isActive = version === v.id;
                return (
                  <button
                    key={v.id}
                    onClick={() => {
                      switchVersion(v.id);
                      setIsOpen(false);
                    }}
                    className={`
                      w-full text-left p-3 rounded-xl text-sm transition-all duration-150
                      flex items-center gap-3 hover:bg-slate-800/80
                      ${isActive ? `bg-slate-800 ${getColorClasses(v.color)}` : 'text-slate-300'}
                    `}
                  >
                    <span className={`w-3 h-3 rounded-full ${getDotColor(v.color, isActive)}`} />
                    <div className="flex-1">
                      <div className="font-medium text-slate-100">{v.name}</div>
                      <div className="text-xs text-slate-500">{v.description}</div>
                    </div>
                    {isActive && (
                      <span className="text-xs text-cyan-400 font-medium">Active</span>
                    )}
                  </button>
                );
              })}
            </div>
            
            <div className="p-3 border-t border-slate-700/50 bg-slate-950/50">
              <div className="text-xs text-slate-500 mb-1">Current API</div>
              <code className="text-xs text-slate-300">
                {currentVersion?.baseUrl}
              </code>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
