import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import {
  WorkflowVersion,
  getWorkflowVersions,
  loadVersionPreference,
  saveVersionPreference,
} from '../config/workflowConfig';

interface WorkflowVersionInfo {
  id: WorkflowVersion;
  name: string;
  description: string;
  color: string;
  baseUrl: string;
}

interface WorkflowVersionContextType {
  version: WorkflowVersion;
  versions: WorkflowVersionInfo[];
  setVersion: (version: WorkflowVersion) => void;
  switchVersion: (version: WorkflowVersion) => void;
}

const WorkflowVersionContext = createContext<WorkflowVersionContextType | undefined>(undefined);

interface WorkflowVersionProviderProps {
  children: ReactNode;
  defaultVersion?: WorkflowVersion;
}

export function WorkflowVersionProvider({ 
  children, 
  defaultVersion 
}: WorkflowVersionProviderProps) {
  const [version, setVersion] = useState<WorkflowVersion>(
    defaultVersion || loadVersionPreference()
  );
  const versions = getWorkflowVersions();

  // Persist version preference when it changes
  useEffect(() => {
    saveVersionPreference(version);
  }, [version]);

  const switchVersion = (newVersion: WorkflowVersion) => {
    setVersion(newVersion);
  };

  const value: WorkflowVersionContextType = {
    version,
    versions,
    setVersion,
    switchVersion,
  };

  return (
    <WorkflowVersionContext.Provider value={value}>
      {children}
    </WorkflowVersionContext.Provider>
  );
}

export function useWorkflowVersion(): WorkflowVersionContextType {
  const context = useContext(WorkflowVersionContext);
  if (context === undefined) {
    throw new Error('useWorkflowVersion must be used within a WorkflowVersionProvider');
  }
  return context;
}

export { WorkflowVersionContext };
