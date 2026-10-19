/* ============================================================
   SOVEREIGN AI WORKBENCH — CONSTANTS
   Canonical status values, types, and labels.
   All values align with backend API contracts.
   ============================================================ */

/** Task execution statuses */
export const TASK_STATUS = {
  CREATED: 'CREATED',
  CLASSIFYING: 'CLASSIFYING',
  ROUTING: 'ROUTING',
  PLANNING: 'PLANNING',
  EXECUTING: 'EXECUTING',
  VERIFYING: 'VERIFYING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
};

/** Agent step statuses */
export const STEP_STATUS = {
  QUEUED: 'QUEUED',
  RUNNING: 'RUNNING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
  DENIED: 'DENIED',
};

/** System health statuses */
export const HEALTH_STATUS = {
  HEALTHY: 'HEALTHY',
  DEGRADED: 'DEGRADED',
  UNAVAILABLE: 'UNAVAILABLE',
};

/** Document processing statuses */
export const DOC_STATUS = {
  UPLOADED: 'UPLOADED',
  PROCESSING: 'PROCESSING',
  INDEXED: 'INDEXED',
  FAILED: 'FAILED',
};

/** Artifact types */
export const ARTIFACT_TYPE = {
  DOCX: 'DOCX',
  XLSX: 'XLSX',
  PDF: 'PDF',
  CODE: 'CODE',
  CALCULATION: 'CALCULATION',
  TEXT: 'TEXT',
};

/** Verification statuses */
export const VERIFICATION_STATUS = {
  VERIFIED: 'VERIFIED',
  UNVERIFIED: 'UNVERIFIED',
  FAILED: 'FAILED',
};

/** Pipeline stages shown in workbench */
export const PIPELINE_STAGES = [
  { key: 'CREATED', label: 'Task Created' },
  { key: 'CLASSIFICATION', label: 'Classification' },
  { key: 'MODEL_ROUTING', label: 'Model Routing' },
  { key: 'PLANNING', label: 'Plan' },
  { key: 'OCR', label: 'OCR Processing' },
  { key: 'RAG_RETRIEVAL', label: 'RAG Retrieval' },
  { key: 'VISION', label: 'Vision Analysis' },
  { key: 'REASONING', label: 'Reasoning' },
  { key: 'ARTIFACT_GENERATION', label: 'Artifact Generation' },
  { key: 'VERIFICATION', label: 'Verification' },
  { key: 'COMPLETED', label: 'Completed' },
];

/** Health service names */
export const HEALTH_SERVICES = [
  { key: 'backend', label: 'Backend API' },
  { key: 'database', label: 'Database' },
  { key: 'model_runtime', label: 'Model Runtime' },
  { key: 'rag', label: 'RAG Engine' },
  { key: 'ocr', label: 'OCR Service' },
  { key: 'vision', label: 'Vision Service' },
  { key: 'tool_registry', label: 'Tool Registry' },
  { key: 'sandbox', label: 'Sandbox' },
  { key: 'security', label: 'Security Module' },
];

/** Navigation items */
export const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: 'LayoutDashboard' },
  { path: '/workbench', label: 'Workbench', icon: 'Wrench' },
  { path: '/documents', label: 'Documents', icon: 'FileText' },
  { path: '/knowledge', label: 'Knowledge Base', icon: 'BookOpen' },
  { path: '/trace', label: 'Agent Trace', icon: 'GitBranch' },
  { path: '/artifacts', label: 'Artifacts', icon: 'Package' },
  { path: '/security', label: 'Security Center', icon: 'Shield' },
  { path: '/models', label: 'Models', icon: 'Cpu' },
  { path: '/health', label: 'System Health', icon: 'Activity' },
];

/** Terminal task states (no more polling) */
export const TERMINAL_STATES = new Set([
  TASK_STATUS.COMPLETED,
  TASK_STATUS.FAILED,
]);

/** Polling interval in ms */
export const POLL_INTERVAL = 2000;
