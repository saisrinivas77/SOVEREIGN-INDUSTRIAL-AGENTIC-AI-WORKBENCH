/* ============================================================
   SOVEREIGN AI WORKBENCH — API SERVICE LAYER
   All frontend-to-backend communication goes through /api/v1/*
   
   SECURITY: This service NEVER calls Ollama, vLLM, ChromaDB,
   SQLite, filesystem, Docker, or any external AI service directly.
   ============================================================ */

const API_BASE = '/api/v1';

/**
 * Safe fetch wrapper with error handling.
 * Never exposes stack traces or internal paths to the UI.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Remove Content-Type for FormData (let browser set boundary)
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const message = errorData?.detail || errorData?.message || `Request failed (${response.status})`;
      throw new ApiError(message, response.status);
    }

    // Handle 204 No Content
    if (response.status === 204) return null;

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    // Network error — safe message, no internals exposed
    throw new ApiError('Unable to connect to backend service. Ensure the system is running.', 0);
  }
}

/** Custom API Error — safe for display */
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

// ── Dashboard ──────────────────────────────────────────────

/** GET /api/v1/dashboard/metrics — All dashboard statistics */
export async function fetchDashboardMetrics() {
  return request('/dashboard/metrics');
}

// ── Tasks ──────────────────────────────────────────────────

/** POST /api/v1/tasks — Create a new task */
export async function createTask(data) {
  let fileIds = data.file_ids || [];

  // If File objects are attached, upload them via /documents/upload first to obtain valid file_ids
  if (data.files && data.files.length > 0) {
    try {
      const uploadRes = await uploadDocuments(data.files);
      if (uploadRes && Array.isArray(uploadRes.uploaded)) {
        const uploadedIds = uploadRes.uploaded
          .map((item) => item?.file?.file_id || item?.document?.file_id || item?.document?.id)
          .filter(Boolean);
        fileIds = [...fileIds, ...uploadedIds];
      }
    } catch (err) {
      console.warn('Document upload warning:', err);
    }
  }

  const payload = {
    instruction: data.instruction,
    file_ids: fileIds,
  };

  const createRes = await request('/tasks', {
    method: 'POST',
    body: JSON.stringify(payload),
  });

  // Automatically trigger task execution run after queuing
  if (createRes && (createRes.task_id || createRes.id)) {
    const taskId = createRes.task_id || createRes.id;
    try {
      await request(`/tasks/${taskId}/run`, { method: 'POST' });
    } catch (runErr) {
      console.warn('Task run execution auto-trigger:', runErr);
    }
  }

  return createRes;
}


/** GET /api/v1/tasks — List all tasks */
export async function fetchTasks() {
  return request('/tasks');
}

/** GET /api/v1/tasks/:id — Get task detail */
export async function fetchTask(taskId) {
  return request(`/tasks/${taskId}`);
}

/** GET /api/v1/tasks/:id/trace — Get agent execution trace */
export async function fetchTaskTrace(taskId) {
  return request(`/tasks/${taskId}/trace`);
}

/** GET /api/v1/tasks/:id/artifacts — Get task artifacts */
export async function fetchTaskArtifacts(taskId) {
  return request(`/tasks/${taskId}/artifacts`);
}

// ── Documents ──────────────────────────────────────────────

/** POST /api/v1/documents/upload — Upload document(s) */
export async function uploadDocuments(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  return request('/documents/upload', {
    method: 'POST',
    body: formData,
  });
}

/** GET /api/v1/documents — List all documents */
export async function fetchDocuments() {
  return request('/documents');
}

/** GET /api/v1/documents/:id — Get document detail */
export async function fetchDocument(docId) {
  return request(`/documents/${docId}`);
}

// ── Knowledge Base / RAG ───────────────────────────────────

/** GET /api/v1/knowledge/search?q=... — Search knowledge base */
export async function searchKnowledge(query) {
  return request(`/knowledge/search?q=${encodeURIComponent(query)}`);
}

// ── Models ─────────────────────────────────────────────────

/** GET /api/v1/models — List available local models */
export async function fetchModels() {
  return request('/models');
}

/** GET /api/v1/models/routing/:task_id — Get model routing info for a task */
export async function fetchModelRouting(taskId) {
  return request(`/models/routing/${taskId}`);
}

// ── Artifacts ──────────────────────────────────────────────

/** GET /api/v1/artifacts — List all generated artifacts */
export async function fetchArtifacts() {
  return request('/artifacts');
}

/** GET /api/v1/artifacts/:id/download — Download artifact */
export function getArtifactDownloadUrl(artifactId) {
  return `${API_BASE}/artifacts/${artifactId}/download`;
}

// ── Security ───────────────────────────────────────────────

/** GET /api/v1/security/telemetry — Security telemetry data */
export async function fetchSecurityTelemetry() {
  return request('/security/telemetry');
}

/** GET /api/v1/security/events — Security event log */
export async function fetchSecurityEvents() {
  return request('/security/events');
}

// ── Reports & PDF Exports ──────────────────────────────────

/** GET /api/v1/reports/pdf — Get downloadable PDF report URL */
export function getReportPdfUrl(reportType = 'task', taskId = null, title = null) {
  let url = `${API_BASE}/reports/pdf?report_type=${encodeURIComponent(reportType)}`;
  if (taskId) url += `&task_id=${encodeURIComponent(taskId)}`;
  if (title) url += `&title=${encodeURIComponent(title)}`;
  return url;
}

/** Trigger direct browser download of PDF report */
export function downloadPdfReport(reportType = 'task', taskId = null, title = null) {
  const url = getReportPdfUrl(reportType, taskId, title);
  const a = document.createElement('a');
  a.href = url;
  a.download = `report_${reportType}${taskId ? '_' + taskId : ''}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// ── System Health ──────────────────────────────────────────

/** GET /api/v1/health — System health status */
export async function fetchHealth() {
  return request('/health');
}

