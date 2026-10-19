import React, { useState } from 'react';
import { GitBranch, RefreshCw } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { fetchTasks, fetchTaskTrace } from '../services/api';
import Timeline from '../components/shared/Timeline';
import StatusBadge from '../components/shared/StatusBadge';
import EmptyState from '../components/shared/EmptyState';
import ErrorState from '../components/shared/ErrorState';
import LoadingState from '../components/shared/LoadingState';
import { formatTimestamp, truncateText } from '../utils/formatters';

/**
 * Royal Blue & White Agent Trace page.
 * Step-by-step audit trail of reasoning, tools, and duration.
 */
export default function TracePage() {
  const { data: tasks, loading: tasksLoading, error: tasksError, refetch: refetchTasks } = useApi(fetchTasks);
  const [selectedTaskId, setSelectedTaskId] = useState(null);
  const { data: traceData, loading: traceLoading, error: traceError, refetch: refetchTrace } = useApi(
    () => selectedTaskId ? fetchTaskTrace(selectedTaskId) : Promise.resolve(null),
    [selectedTaskId]
  );

  const taskList = Array.isArray(tasks) ? tasks : tasks?.tasks || [];

  if (tasksLoading) return <LoadingState message="Loading agent task history…" />;
  if (tasksError) return <ErrorState message={tasksError} onRetry={refetchTasks} />;

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <span className="gradient-text">Agent Execution Trace & Audit</span>
          </h1>
          <p className="page-subtitle">Inspect every tool invocation, action, and reasoning step</p>
        </div>
        <button className="btn btn-glass btn-sm" onClick={refetchTasks}>
          <RefreshCw size={13} />
          <span>Refresh</span>
        </button>
      </div>

      {taskList.length === 0 ? (
        <EmptyState
          icon={GitBranch}
          title="No Executed Tasks"
          message="Run an engineering task in the Workbench to inspect its step-by-step reasoning trace here."
        />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 'var(--space-5)', minHeight: '450px' }}>
          {/* Task List Column */}
          <div className="card" style={{ padding: 'var(--space-3)', overflow: 'auto', maxHeight: '72vh' }}>
            <div className="section-title" style={{ padding: 'var(--space-2)' }}>
              Execution Tasks
            </div>
            {taskList.map((task) => {
              const taskId = task.id || task.task_id;
              const isSelected = selectedTaskId === taskId;

              return (
                <button
                  key={taskId}
                  onClick={() => setSelectedTaskId(taskId)}
                  style={{
                    display: 'block',
                    width: '100%',
                    textAlign: 'left',
                    padding: 'var(--space-3)',
                    borderRadius: 'var(--radius-md)',
                    marginBottom: 'var(--space-2)',
                    background: isSelected ? 'var(--color-accent-light)' : 'transparent',
                    border: isSelected
                      ? '1.5px solid var(--color-accent-primary)'
                      : '1px solid transparent',
                    cursor: 'pointer',
                    transition: 'all var(--transition-fast)',
                    boxShadow: isSelected ? '0 2px 8px rgba(30, 64, 175, 0.1)' : 'none',
                  }}
                >
                  <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 'var(--space-1)' }}>
                    {truncateText(task.instruction || task.description || 'Task Analysis', 50)}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)' }}>
                      {formatTimestamp(task.created_at)}
                    </span>
                    <StatusBadge status={task.status} />
                  </div>
                </button>
              );
            })}
          </div>

          {/* Trace Detail Column */}
          <div className="card" style={{ overflow: 'auto', maxHeight: '72vh' }}>
            {!selectedTaskId ? (
              <EmptyState message="Select an agent task on the left to inspect its execution timeline." />
            ) : traceLoading ? (
              <LoadingState message="Loading step trace details…" />
            ) : traceError ? (
              <ErrorState message={traceError} onRetry={refetchTrace} />
            ) : !traceData || !(traceData.steps || traceData)?.length ? (
              <EmptyState message="No execution steps recorded for this task." />
            ) : (
              <div>
                <div className="section-title" style={{ marginBottom: 'var(--space-4)' }}>
                  Execution Timeline ({(traceData.steps || traceData).length} steps)
                </div>
                <Timeline steps={traceData.steps || traceData} />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
