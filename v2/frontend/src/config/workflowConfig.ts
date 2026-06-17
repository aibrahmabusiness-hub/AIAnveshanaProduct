/**
 * Workflow Version Configuration
 * Allows switching between v1 (legacy) and v2 (new) workflow engines
 */

export type WorkflowVersion = 'v1' | 'v2';

// API base URLs for each version
export const WORKFLOW_API_CONFIG = {
  v1: {
    baseUrl: '', // relative path
    name: 'Legacy (v1)',
    description: 'Original Drawflow-based workflow engine',
    color: 'amber',
  },
  v2: {
    baseUrl: '', // relative path
    name: 'Ultra-Lightweight (v2)',
    description: 'New React Flow + Celery workflow engine',
    color: 'cyan',
  },
} as Record<WorkflowVersion, { baseUrl: string; name: string; description: string; color: string; }>;

// Default version
export const DEFAULT_VERSION: WorkflowVersion = 'v2';

// Storage key for persisting user's version preference
export const WORKFLOW_VERSION_STORAGE_KEY = 'workflow_version_preference';

/**
 * Get the current API base URL based on the selected version
 */
export function getApiBaseUrl(version: WorkflowVersion): string {
  return WORKFLOW_API_CONFIG[version].baseUrl;
}

/**
 * Get WebSocket URL for the selected version
 */
export function getWebSocketUrl(version: WorkflowVersion, workflowId?: string): string {
  let baseUrl = WORKFLOW_API_CONFIG[version].baseUrl;
  if (!baseUrl) {
    // Determine the current host dynamically for relative paths
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    baseUrl = `${protocol}//${window.location.host}`;
  } else {
    baseUrl = baseUrl.replace(/^http/, 'ws');
  }
  const wsBase = baseUrl;
  
  if (workflowId) {
    return `${wsBase}/ws/logs?workflow_id=${workflowId}`;
  }
  return `${wsBase}/ws/logs`;
}

/**
 * Get all available versions
 */
export function getWorkflowVersions() {
  return Object.entries(WORKFLOW_API_CONFIG).map(([key, config]) => ({
    id: key as WorkflowVersion,
    ...config,
  }));
}

/**
 * Save user's version preference to localStorage
 */
export function saveVersionPreference(version: WorkflowVersion): void {
  localStorage.setItem(WORKFLOW_VERSION_STORAGE_KEY, version);
}

/**
 * Load user's version preference from localStorage
 */
export function loadVersionPreference(): WorkflowVersion {
  const saved = localStorage.getItem(WORKFLOW_VERSION_STORAGE_KEY);
  return (saved as WorkflowVersion) || DEFAULT_VERSION;
}
