// Flow Types for React Flow
import { Node, Edge } from '@xyflow/react';

// Execution status types
export interface NodeExecutionStatus {
  [nodeId: string]: {
    status: 'idle' | 'running' | 'success' | 'error';
    message?: string;
    error?: string;
  };
}

export interface WorkflowExecutionState {
  isExecuting: boolean;
  currentNodeId?: string;
  taskId?: string;
}

// Piece definition
export interface Piece {
  name: string;
  displayName: string;
  category: string;
  description: string;
  icon?: string;
}

// Project definition
export interface Project {
  id: string;
  name: string;
  nodes: Node[];
  edges: Edge[];
}
