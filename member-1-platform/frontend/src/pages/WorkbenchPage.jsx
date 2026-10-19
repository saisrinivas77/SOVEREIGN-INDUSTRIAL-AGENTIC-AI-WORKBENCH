import React, { useState, useCallback, useRef } from 'react';
import {
  Play, Loader, ChevronRight, CheckCircle2, XCircle, Clock, CircleDot,
  Paperclip, Mic, Sparkles, Cpu, Eye, FileText, ArrowUp, AlertCircle,
  FileCheck, Shield, Layers, RefreshCw, Zap, Download
} from 'lucide-react';
import { useTaskExecution } from '../hooks/useTaskExecution';
import { downloadPdfReport, getArtifactDownloadUrl } from '../services/api';
import FileUpload from '../components/shared/FileUpload';
import Timeline from '../components/shared/Timeline';
import StatusBadge from '../components/shared/StatusBadge';
import { PIPELINE_STAGES, TERMINAL_STATES } from '../utils/constants';
import { formatTimestamp, formatFileSize } from '../utils/formatters';


const SUGGESTED_PROMPTS = [
  {
    icon: Eye,
    color: '#0284c7',
    title: 'Radiography Defect Analysis',
    prompt: 'Inspect this pipeline weld radiograph image, detect porosity or crack defects, and draft a technical approval memo.',
    taskType: 'VISION + OCR',
  },
  {
    icon: FileText,
    color: '#1e40af',
    title: 'Turbine Vibration Inspection',
    prompt: 'Analyze the turbine sensor log and thermal inspection report. Correlate with historical RAG threshold standards and prepare an engineering sign-off.',
    taskType: 'RAG + ANALYSIS',
  },
  {
    icon: Shield,
    color: '#059669',
    title: 'PSU Compliance & Safety Audit',
    prompt: 'Cross-verify the equipment maintenance certificate against PSU industrial safety mandates (IS-1239/ASME) and identify discrepancies.',
    taskType: 'REASONING',
  },
  {
    icon: Layers,
    color: '#7c3aed',
    title: 'P&ID Flow Diagram Audit',
    prompt: 'Extract instrumentation tags and valve line specs from the attached P&ID drawing, verify hazardous safety margins, and output an XLSX audit sheet.',
    taskType: 'VISION + ARTIFACT',
  },
];

const LOCAL_MODELS = [
  { id: 'qwen2.5:7b', name: 'qwen2.5:7b', type: 'Reasoning + General' },
  { id: 'qwen2.5-coder:7b', name: 'qwen2.5-coder:7b', type: 'Coding + General' },
  { id: 'llama3.2-vision:11b', name: 'llama3.2-vision:11b', type: 'Vision + Multimodal' },
  { id: 'qwen2-vl:7b', name: 'Qwen2-VL 7B (Multimodal)', type: 'Vision + OCR' },
];


/**
 * Royal Blue & White Sovereign AI Workbench.
 * Clean, enterprise workspace with suggested prompt cards, floating AI input,
 * voice toggle, model router, and real-time execution telemetry.
 */
export default function WorkbenchPage() {
  const [instruction, setInstruction] = useState('');
  const [files, setFiles] = useState([]);
  const [selectedModel, setSelectedModel] = useState(LOCAL_MODELS[0].id);
  const [isRecording, setIsRecording] = useState(false);
  const fileInputRef = useRef(null);

  const {
    activeTaskId, startTask, clearTask,
    creating, createError,
    taskData, taskLoading, taskError,
    traceData, traceLoading,
    isPolling,
  } = useTaskExecution();

  const handleSubmit = useCallback(async (e) => {
    if (e) e.preventDefault();
    if (!instruction.trim()) return;
    try {
      await startTask(instruction.trim(), files);
    } catch {
      // Handled via createError
    }
  }, [instruction, files, startTask]);

  const handlePromptSelect = (promptText) => {
    setInstruction(promptText);
  };

  const handleNewTask = useCallback(() => {
    clearTask();
    setInstruction('');
    setFiles([]);
  }, [clearTask]);

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording && !instruction) {
      setInstruction('Analyze the attached industrial inspection report for crack defects and generate a signed verification summary.');
    }
  };

  return (
    <div className="animate-fade-in">
      {/* ── Page Header ── */}
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <span className="gradient-text">Industrial AI Workbench</span>
          </h1>
          <p className="page-subtitle">
            Autonomous agentic processing on air-gapped local multimodal LLMs
          </p>
        </div>

        {activeTaskId && (
          <button className="btn btn-glass" onClick={handleNewTask}>
            <RefreshCw size={14} />
            Start New Task
          </button>
        )}
      </div>

      {/* ── View 1: Task Creation (Welcome & Input Area) ── */}
      {!activeTaskId && (
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          {/* Welcome Headline */}
          <div style={{ textAlign: 'center', margin: 'var(--space-6) 0 var(--space-8)' }}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 'var(--space-2)',
              padding: '5px 14px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--color-accent-light)',
              border: '1px solid rgba(30, 64, 175, 0.2)',
              color: 'var(--color-accent-primary)',
              fontSize: 'var(--text-xs)',
              fontWeight: 700,
              marginBottom: 'var(--space-4)'
            }}>
              <Sparkles size={13} />
              100% LOCAL MULTIMODAL AGENT RUNTIME
            </div>

            <h2 style={{ fontSize: 'var(--text-3xl)', fontWeight: 800, color: 'var(--color-text-primary)', letterSpacing: '-0.03em', marginBottom: 'var(--space-2)' }}>
              What confidential analysis do you need today?
            </h2>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-md)', maxWidth: '580px', margin: '0 auto' }}>
              Upload technical drawings, telemetry logs, or inspection images. Our sovereign agents execute OCR, RAG, and verification on-premise.
            </p>
          </div>

          {/* ── Advanced Floating AI Input Container ── */}
          <form onSubmit={handleSubmit} style={{ marginBottom: 'var(--space-8)' }}>
            <div className="ai-input-wrapper">
              <textarea
                className="ai-input-area"
                placeholder="Enter industrial instruction... (e.g. 'Analyze this boiler inspection radiograph and prepare an ASME approval note')"
                value={instruction}
                onChange={(e) => setInstruction(e.target.value)}
                rows={2}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
              />

              {/* Attached Files Chips */}
              {files && files.length > 0 && (
                <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap', margin: 'var(--space-2) 0' }}>
                  {files.map((file, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--space-2)',
                        padding: '4px 10px',
                        background: 'var(--color-accent-light)',
                        border: '1px solid rgba(37, 99, 235, 0.2)',
                        borderRadius: 'var(--radius-full)',
                        fontSize: 'var(--text-xs)',
                        color: 'var(--color-accent-primary)',
                        fontWeight: 500,
                      }}
                    >
                      <Paperclip size={12} />
                      <span className="truncate" style={{ maxWidth: '160px' }}>{file.name}</span>
                      <span style={{ opacity: 0.6, fontSize: '10px' }}>({formatFileSize(file.size)})</span>
                      <button
                        type="button"
                        onClick={() => {
                          const updated = [...files];
                          updated.splice(idx, 1);
                          setFiles(updated);
                        }}
                        style={{ color: 'var(--color-text-tertiary)', padding: 0, lineHeight: 1 }}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Bottom Controls */}
              <div className="ai-input-controls">
                <div className="ai-input-left">
                  {/* Model Selector Pill */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--space-1)',
                      padding: '4px 10px',
                      background: '#f8fafc',
                      border: '1px solid var(--color-border-default)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--text-xs)',
                      color: 'var(--color-text-secondary)',
                    }}>
                      <Cpu size={13} style={{ color: 'var(--color-accent-primary)' }} />
                      <select
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          padding: 0,
                          fontSize: 'var(--text-xs)',
                          color: 'var(--color-text-primary)',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        {LOCAL_MODELS.map((m) => (
                          <option key={m.id} value={m.id} style={{ background: '#ffffff', color: '#0f172a' }}>
                            {m.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Attach Button */}
                  <input
                    type="file"
                    ref={fileInputRef}
                    multiple
                    style={{ display: 'none' }}
                    onChange={(e) => {
                      const selected = Array.from(e.target.files);
                      if (selected.length > 0) setFiles([...files, ...selected]);
                      e.target.value = '';
                    }}
                  />
                  <button
                    type="button"
                    className="btn-icon btn-sm"
                    onClick={() => fileInputRef.current?.click()}
                    title="Attach technical documents or images"
                  >
                    <Paperclip size={16} />
                  </button>

                  {/* Voice Button */}
                  <button
                    type="button"
                    className={`btn-icon btn-sm ${isRecording ? 'text-accent' : ''}`}
                    onClick={toggleRecording}
                    title={isRecording ? 'Listening (click to stop)' : 'Voice dictation'}
                    style={isRecording ? { background: 'var(--color-accent-light)', borderRadius: 'var(--radius-full)' } : {}}
                  >
                    {isRecording ? (
                      <div className="voice-wave">
                        <div className="voice-bar" />
                        <div className="voice-bar" />
                        <div className="voice-bar" />
                        <div className="voice-bar" />
                      </div>
                    ) : (
                      <Mic size={16} />
                    )}
                  </button>
                </div>

                {/* Right: Submit Button */}
                <div className="ai-input-right">
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={creating || !instruction.trim()}
                    style={{ borderRadius: 'var(--radius-full)', padding: '0.5rem 1.35rem' }}
                  >
                    {creating ? (
                      <>
                        <Loader size={15} className="animate-spin" />
                        <span>Initializing Agent…</span>
                      </>
                    ) : (
                      <>
                        <span>Execute Plan</span>
                        <ArrowUp size={15} />
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {createError && (
              <div style={{
                marginTop: 'var(--space-3)',
                padding: 'var(--space-3) var(--space-4)',
                background: 'var(--color-status-failed-bg)',
                border: '1px solid var(--color-status-failed-border)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--color-status-failed)',
                fontSize: 'var(--text-sm)',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-2)',
              }}>
                <AlertCircle size={16} />
                <span>{createError}</span>
              </div>
            )}
          </form>

          {/* ── Suggested Scenarios Grid ── */}
          <div style={{ marginBottom: 'var(--space-10)' }}>
            <div style={{
              fontSize: 'var(--text-xs)',
              fontWeight: 700,
              color: 'var(--color-accent-primary)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 'var(--space-3)'
            }}>
              Suggested Industrial Scenarios
            </div>

            <div className="prompt-grid">
              {SUGGESTED_PROMPTS.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <div
                    key={idx}
                    className="prompt-card"
                    onClick={() => handlePromptSelect(item.prompt)}
                  >
                    <div>
                      <div className="prompt-card-icon" style={{ background: `${item.color}15`, color: item.color }}>
                        <Icon size={18} />
                      </div>
                      <div className="prompt-card-title">{item.title}</div>
                      <div className="prompt-card-sub">{item.prompt}</div>
                    </div>

                    <div style={{
                      marginTop: 'var(--space-3)',
                      fontSize: '10px',
                      fontFamily: 'var(--font-mono)',
                      color: item.color,
                      fontWeight: 700
                    }}>
                      {item.taskType}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ── View 2: Live Execution Monitor ── */}
      {activeTaskId && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 'var(--space-6)' }}>
          {/* Main Column */}
          <div>
            {/* Task Card Header */}
            <div className="card" style={{ marginBottom: 'var(--space-5)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--space-4)' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                    <span className="mono" style={{ fontSize: 'var(--text-xs)', color: 'var(--color-accent-primary)', fontWeight: 700 }}>
                      TASK #{activeTaskId}
                    </span>
                    <span style={{ color: 'var(--color-border-strong)' }}>•</span>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)' }}>
                      {formatTimestamp(taskData?.created_at)}
                    </span>
                  </div>

                  <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                    {instruction}
                  </h2>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => downloadPdfReport('task', activeTaskId, instruction)}
                    title="Download Analysis Report in PDF format"
                  >
                    <Download size={13} />
                    <span>Download PDF Report</span>
                  </button>

                  {isPolling && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--space-1)',
                      padding: '3px 8px',
                      borderRadius: 'var(--radius-full)',
                      background: 'var(--color-status-running-bg)',
                      color: 'var(--color-status-running)',
                      fontSize: 'var(--text-xs)',
                      fontWeight: 700,
                    }}>
                      <Loader size={12} className="animate-spin" />
                      <span>LIVE</span>
                    </div>
                  )}
                  <StatusBadge status={taskData?.status || 'RUNNING'} />
                </div>
              </div>
            </div>

            {/* Agent Trace Timeline */}
            <div className="section">
              <div className="card-header">
                <span className="card-title">Live Agent Timeline</span>
                <span className="text-xs text-secondary">
                  {traceData?.steps?.length || 0} step{(traceData?.steps?.length !== 1) ? 's' : ''} executed
                </span>
              </div>

              {traceData?.steps && traceData.steps.length > 0 ? (
                <Timeline steps={traceData.steps} />
              ) : (
                <div style={{ padding: 'var(--space-8)', textAlign: 'center', background: '#ffffff', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border-subtle)' }}>
                  <div className="spinner" style={{ margin: '0 auto var(--space-3)' }} />
                  <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', fontWeight: 500 }}>
                    Agent decomposing instruction and formulating execution plan…
                  </div>
                </div>
              )}
            </div>

            {/* Generated Artifacts */}
            {taskData?.artifacts && taskData.artifacts.length > 0 && (
              <div className="section">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-3)' }}>
                  <span className="section-title" style={{ margin: 0 }}>Verified Artifacts</span>
                  <button
                    className="btn btn-glass btn-sm"
                    onClick={() => downloadPdfReport('task', activeTaskId, instruction)}
                  >
                    <Download size={13} />
                    <span>Download All (PDF)</span>
                  </button>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                  {taskData.artifacts.map((art, idx) => (
                    <div className="card" key={art.id || art.artifact_id || idx} style={{ padding: 'var(--space-4)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                          <FileCheck size={20} style={{ color: 'var(--color-status-healthy)' }} />
                          <div>
                            <div style={{ fontWeight: 600 }}>{art.filename}</div>
                            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)' }}>
                              Type: {art.type.toUpperCase()} {art.sha256 ? `• SHA256: ${art.sha256.slice(0, 12)}…` : ''}
                            </div>
                          </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                          <a
                            className="btn btn-glass btn-sm"
                            href={getArtifactDownloadUrl(art.artifact_id || art.id)}
                            download={art.filename}
                            style={{ textDecoration: 'none' }}
                          >
                            <Download size={12} />
                            <span>Download {art.type.toUpperCase()}</span>
                          </a>
                          <StatusBadge status={art.verification_status || 'VERIFIED'} />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>

          {/* Right Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {/* Pipeline Stage Tracker */}
            <div className="card">
              <div className="card-header">
                <span className="card-title">Pipeline Progress</span>
              </div>

              <div className="pipeline-track">
                {PIPELINE_STAGES.map((stage, idx) => {
                  const currentStage = taskData?.current_stage || taskData?.status;
                  const stageIdx = PIPELINE_STAGES.findIndex((s) => s.key === currentStage);
                  const pipeIdx = idx;
                  let stageStatus = 'pending';

                  if (taskData?.status === 'FAILED') {
                    if (pipeIdx < stageIdx) stageStatus = 'completed';
                    else if (pipeIdx === stageIdx) stageStatus = 'failed';
                  } else if (taskData?.status === 'COMPLETED') {
                    stageStatus = 'completed';
                  } else {
                    if (pipeIdx < stageIdx) stageStatus = 'completed';
                    else if (pipeIdx === stageIdx) stageStatus = 'running';
                  }

                  return (
                    <div
                      key={stage.key}
                      className={`pipeline-node pipeline-node--${stageStatus}`}
                    >
                      {stageStatus === 'completed' && <CheckCircle2 size={16} style={{ color: 'var(--color-status-completed)', flexShrink: 0 }} />}
                      {stageStatus === 'running' && <Loader size={16} className="animate-spin" style={{ color: 'var(--color-status-running)', flexShrink: 0 }} />}
                      {stageStatus === 'failed' && <XCircle size={16} style={{ color: 'var(--color-status-failed)', flexShrink: 0 }} />}
                      {stageStatus === 'pending' && <CircleDot size={16} style={{ color: 'var(--color-text-tertiary)', opacity: 0.5, flexShrink: 0 }} />}

                      <div style={{ flex: 1 }}>
                        <div style={{
                          fontSize: 'var(--text-xs)',
                          fontWeight: stageStatus === 'running' ? 700 : 500,
                          color: stageStatus === 'pending' ? 'var(--color-text-tertiary)' : 'var(--color-text-primary)'
                        }}>
                          {stage.label}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Model Routing Intelligence */}
            <div className="card">
              <div className="card-header">
                <span className="card-title">Model Router Decision</span>
                <Zap size={14} style={{ color: 'var(--color-accent-primary)' }} />
              </div>

              <dl className="routing-card" style={{ fontSize: 'var(--text-xs)' }}>
                <dt>Task Type</dt>
                <dd>{taskData?.routing?.task_type || 'MULTIMODAL'}</dd>
                <dt>Routed Model</dt>
                <dd style={{ color: 'var(--color-accent-primary)' }}>
                  {taskData?.routing?.model || 'Qwen2-VL 7B'}
                </dd>
                <dt>Runtime</dt>
                <dd style={{ color: 'var(--color-status-healthy)' }}>
                  LOCAL (GPU 0)
                </dd>
                <dt>Reason</dt>
                <dd style={{ color: 'var(--color-text-secondary)' }}>
                  {taskData?.routing?.reason || 'Visual OCR + table extraction required on-premise.'}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
