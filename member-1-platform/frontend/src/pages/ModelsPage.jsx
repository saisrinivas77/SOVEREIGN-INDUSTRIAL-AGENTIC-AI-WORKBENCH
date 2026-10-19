import React, { useEffect } from 'react';
import { Cpu, RefreshCw, Server, Zap, CheckCircle2 } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { fetchModels, fetchTasks } from '../services/api';
import StatusBadge from '../components/shared/StatusBadge';
import EmptyState from '../components/shared/EmptyState';
import ErrorState from '../components/shared/ErrorState';
import LoadingState from '../components/shared/LoadingState';

/**
 * Royal Blue & White Models Page.
 * Available local models and real-time routing decisions.
 */
export default function ModelsPage() {
  const { data: modelsData, loading, error, refetch: refetchModels } = useApi(fetchModels);
  const { data: tasksData, refetch: refetchTasks } = useApi(fetchTasks);

  useEffect(() => {
    const timer = setInterval(() => {
      refetchModels();
      refetchTasks();
    }, 5000);
    return () => clearInterval(timer);
  }, [refetchModels, refetchTasks]);

  if (loading) return <LoadingState message="Querying local model registry…" />;
  if (error) return <ErrorState message={error} onRetry={refetchModels} />;

  const models = Array.isArray(modelsData) ? modelsData : modelsData?.models || [];
  const tasks = Array.isArray(tasksData) ? tasksData : tasksData?.tasks || [];

  const routingDecisions = tasks
    .filter((t) => t.task_type || t.routing)
    .slice(0, 10)
    .map((t) => ({
      task: t.instruction || t.description || 'Task',
      task_type: t.task_type || t.routing?.task_type || 'general',
      model: t.selected_model || t.routing?.model_id || t.routing?.model || 'qwen2.5:7b',
      runtime: 'LOCAL',
      reason: t.routing?.reason || `Routed to local ${t.task_type || 'general'} capability model`,
    }));

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <span className="gradient-text">Local Model Catalog & Routing</span>
          </h1>
          <p className="page-subtitle">On-premise open-weight LLMs and router telemetry</p>
        </div>
        <button
          className="btn btn-glass btn-sm"
          onClick={() => {
            refetchModels();
            refetchTasks();
          }}
        >
          <RefreshCw size={13} />
          <span>Refresh</span>
        </button>
      </div>

      {/* ── Available Models Grid ── */}
      <div className="section">
        <div className="card-header">
          <span className="card-title">Available Local Models ({models.length})</span>
        </div>

        {models.length === 0 ? (
          <EmptyState
            icon={Cpu}
            title="No Models Registered"
            message="No local model instances detected. Ensure Ollama runtime is active."
          />
        ) : (
          <div className="grid-cards">
            {models.map((model, idx) => (
              <div className="card animate-fade-in" key={model.model_id || model.id || idx} style={{ animationDelay: `${idx * 50}ms` }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)', marginBottom: 'var(--space-3)' }}>
                  <div style={{
                    width: 44, height: 44,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-accent-light)',
                    color: 'var(--color-accent-primary)',
                    flexShrink: 0,
                  }}>
                    <Cpu size={22} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 700, color: 'var(--color-text-primary)', wordBreak: 'break-word', fontSize: 'var(--text-md)' }}>
                      {model.model_id || model.name || 'Unknown Model'}
                    </div>
                    {model.context_limit && (
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)', marginTop: 2 }}>
                        Context Limit: {model.context_limit.toLocaleString()} tokens
                      </div>
                    )}
                  </div>
                  <StatusBadge status={model.available ? 'HEALTHY' : 'UNAVAILABLE'} />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', fontSize: 'var(--text-xs)' }}>
                  {model.capabilities && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--color-text-tertiary)' }}>Capabilities</span>
                      <span style={{ fontWeight: 600, color: 'var(--color-accent-primary)' }}>
                        {Array.isArray(model.capabilities) ? model.capabilities.join(', ') : model.capabilities}
                      </span>
                    </div>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-tertiary)' }}>Status / Engine</span>
                    <span style={{ fontWeight: 600, color: 'var(--color-status-healthy)' }}>
                      {model.health || 'ready'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-tertiary)' }}>Runtime</span>
                    <span style={{ color: 'var(--color-status-healthy)', fontWeight: 700 }}>
                      <Server size={10} style={{ display: 'inline', marginRight: 4 }} />
                      LOCAL
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Recent Routing Decisions ── */}
      {routingDecisions.length > 0 && (
        <div className="section">
          <div className="card-header">
            <span className="card-title">Recent Router Decisions</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {routingDecisions.map((rd, idx) => (
              <div className="card" key={idx} style={{ padding: 'var(--space-4)' }}>
                <div style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 'var(--space-3)' }}>
                  {rd.task}
                </div>
                <dl className="routing-card">
                  <dt>Task Type</dt>
                  <dd>{rd.task_type ? rd.task_type.toUpperCase() : '—'}</dd>
                  <dt>Selected Model</dt>
                  <dd style={{ color: 'var(--color-accent-primary)', fontWeight: 700 }}>
                    <Zap size={12} style={{ display: 'inline', marginRight: 4 }} />
                    {rd.model || '—'}
                  </dd>
                  <dt>Runtime</dt>
                  <dd style={{ color: 'var(--color-status-healthy)', fontWeight: 700 }}>{rd.runtime || 'LOCAL'}</dd>
                  <dt>Reason</dt>
                  <dd>{rd.reason || '—'}</dd>
                </dl>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
