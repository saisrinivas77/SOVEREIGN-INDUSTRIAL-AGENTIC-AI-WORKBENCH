/**
 * SOVEREIGN AI WORKBENCH — DATA SCHEMAS
 * JSDoc type definitions matching backend API contracts.
 * These types are for documentation only — they mirror the backend schemas.
 *
 * IMPORTANT: These schemas are defined by the backend team.
 * Frontend MUST NOT invent schemas. If a field is missing from the
 * backend response, display "—" rather than fabricating data.
 */

/**
 * @typedef {Object} Task
 * @property {string} id - Unique task identifier
 * @property {string} instruction - User's task instruction
 * @property {string} status - CREATED|CLASSIFYING|ROUTING|PLANNING|EXECUTING|VERIFYING|COMPLETED|FAILED
 * @property {string} [current_stage] - Current pipeline stage key
 * @property {string} created_at - ISO timestamp
 * @property {string} [completed_at] - ISO timestamp
 * @property {TaskRouting} [routing] - Model routing decision
 * @property {Artifact[]} [artifacts] - Generated artifacts
 */

/**
 * @typedef {Object} TaskRouting
 * @property {string} task_type - e.g. VISION, TEXT, ANALYSIS
 * @property {string} model - Selected model name
 * @property {string} runtime - LOCAL
 * @property {string} reason - Routing rationale
 */

/**
 * @typedef {Object} TraceStep
 * @property {string} step_id - Unique step ID
 * @property {number} step_number - Sequential step number
 * @property {string} action - Action description
 * @property {string} [tool] - Tool used
 * @property {string} status - QUEUED|RUNNING|COMPLETED|FAILED|DENIED
 * @property {string} timestamp - ISO timestamp
 * @property {number} [duration] - Duration in seconds
 * @property {string} [result_summary] - Safe result summary
 * @property {string} [error] - Error message (only for FAILED)
 */

/**
 * @typedef {Object} Document
 * @property {string} document_id - Unique document ID
 * @property {string} filename - Display filename (no paths)
 * @property {string} type - File type
 * @property {number} size - Size in bytes
 * @property {string} processing_status - Processing status
 * @property {string} ocr_status - OCR status
 * @property {string} index_status - Index status
 */

/**
 * @typedef {Object} KnowledgeChunk
 * @property {string} [chunk_id] - Chunk identifier
 * @property {string} document - Source document name
 * @property {number} [page] - Page number
 * @property {string} [section] - Section heading
 * @property {number} [chunk] - Chunk index
 * @property {number} relevance_score - 0–1 relevance score
 * @property {string} excerpt - Source excerpt text
 */

/**
 * @typedef {Object} Artifact
 * @property {string} id - Artifact ID
 * @property {string} filename - Display filename
 * @property {string} type - DOCX|XLSX|PDF|CODE|CALCULATION|TEXT
 * @property {string} created_at - ISO timestamp
 * @property {string} verification_status - VERIFIED|UNVERIFIED|FAILED
 * @property {string} [hash] - Content hash
 */

/**
 * @typedef {Object} SecurityTelemetry
 * @property {string} network_mode - e.g. SOVEREIGN MODE, RESTRICTED
 * @property {number} external_ai_calls
 * @property {number} external_calls
 * @property {number} blocked_attempts
 * @property {number} local_model_calls
 * @property {number} local_tool_calls
 * @property {number} local_rag_calls
 */

/**
 * @typedef {Object} SecurityEvent
 * @property {string} [id]
 * @property {string} timestamp
 * @property {string} type
 * @property {string} description
 * @property {string} severity - LOW|MEDIUM|HIGH|CRITICAL
 */

/**
 * @typedef {Object} HealthStatus
 * @property {Object.<string, string>} services - Map of service key to HEALTHY|DEGRADED|UNAVAILABLE
 * @property {string} [timestamp] - ISO timestamp of last check
 */

/**
 * @typedef {Object} Model
 * @property {string} [id]
 * @property {string} name - Model display name
 * @property {string} [variant] - Model variant/size
 * @property {string[]} [capabilities] - List of capabilities
 * @property {string} [size] - Model size description
 * @property {string} [status] - HEALTHY|UNAVAILABLE
 */

/**
 * @typedef {Object} DashboardMetrics
 * @property {number} active_tasks
 * @property {number} completed_tasks
 * @property {number} failed_tasks
 * @property {number} indexed_documents
 * @property {number} available_models
 * @property {number} generated_artifacts
 * @property {number} security_events
 * @property {number} external_calls
 * @property {number} blocked_calls
 */

export {};
