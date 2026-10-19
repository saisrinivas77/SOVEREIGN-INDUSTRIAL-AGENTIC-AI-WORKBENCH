import React, { useEffect } from 'react';
import {
  Shield, ShieldAlert, ShieldCheck, Wifi, WifiOff,
  Globe, Ban, Server, Database, Eye, RefreshCw, Lock, Zap, Download
} from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { fetchSecurityTelemetry, fetchSecurityEvents, downloadPdfReport } from '../services/api';
import SovereignBadge from '../components/shared/SovereignBadge';
import StatusBadge from '../components/shared/StatusBadge';
import ErrorState from '../components/shared/ErrorState';
import LoadingState from '../components/shared/LoadingState';
import EmptyState from '../components/shared/EmptyState';
import { formatTimestamp } from '../utils/formatters';

/**
 * Royal Blue & White Security Center.
 * Demonstrates 100% On-Premise Sovereign Operation Proof with live backend telemetry.
 */
export default function SecurityPage() {
  const { data: telemetry, loading: telLoading, error: telError, refetch: refetchTel } = useApi(fetchSecurityTelemetry);
  const { data: eventsData, loading: evLoading, error: evError, refetch: refetchEv } = useApi(fetchSecurityEvents);

  useEffect(() => {
    const timer = setInterval(() => {
      refetchTel();
      refetchEv();
    }, 4000);
    return () => clearInterval(timer);
  }, [refetchTel, refetchEv]);

  if (telLoading) return <LoadingState message="Connecting to secure audit bus…" />;
  if (telError) return <ErrorState message={telError} onRetry={refetchTel} />;

  const t = telemetry || {};
  const events = Array.isArray(eventsData) ? eventsData : eventsData?.events || [];

  return (
    <div className="animate-fade-in">
      {/* ── Top Header ── */}
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <span className="gradient-text">Security & Sovereignty Center</span>
          </h1>
          <p className="page-subtitle">Hardware-level isolation and network egress prevention audit</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => downloadPdfReport('security', null, 'Sovereign Security & Compliance Audit')}
          >
            <Download size={13} />
            <span>Export Security Audit (PDF)</span>
          </button>
          <button className="btn btn-glass btn-sm" onClick={() => { refetchTel(); refetchEv(); }}>
            <RefreshCw size={13} />
            <span>Audit Refresh</span>
          </button>
          <SovereignBadge mode={t.network_mode || 'SOVEREIGN MODE'} />
        </div>
      </div>


      {/* ── Sovereign Shield Banner (Royal Blue & White) ── */}
      <div className="card" style={{
        marginBottom: 'var(--space-8)',
        background: 'linear-gradient(135deg, #eff6ff 0%, #ffffff 100%)',
        borderColor: 'rgba(37, 99, 235, 0.25)',
        boxShadow: 'var(--shadow-md)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-5)', flexWrap: 'wrap' }}>
          <div style={{
            width: 64,
            height: 64,
            borderRadius: 'var(--radius-xl)',
            background: 'var(--color-accent-primary)',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(30, 64, 175, 0.3)'
          }}>
            <ShieldCheck size={36} />
          </div>

          <div style={{ flex: 1, minWidth: '240px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span style={{ fontSize: 'var(--text-xl)', fontWeight: 800, color: 'var(--color-accent-primary)' }}>
                {t.network_mode || 'SOVEREIGN MODE'}
              </span>
              <span className="status-badge status-badge--healthy">ACTIVE ENFORCEMENT</span>
            </div>
            <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              Zero-Trust Local Perimeter: Direct socket inspection prevents any outbound OpenAI/Anthropic/Google/Cloud AI calls.
            </div>
          </div>
        </div>
      </div>

      {/* ── Live Telemetry Grid ── */}
      <div className="section">
        <div className="card-header">
          <span className="card-title">Live Sovereign Telemetry</span>
          <span className="text-xs text-secondary font-medium">Verified by Kernel Netfilter</span>
        </div>

        <div className="telemetry-grid">
          <div className="telemetry-item">
            <div className="telemetry-label">
              <Globe size={13} style={{ color: 'var(--color-accent-primary)' }} />
              <span>External AI Calls</span>
            </div>
            <div className={`telemetry-value ${(t.external_ai_calls || 0) === 0 ? 'telemetry-value--safe' : 'telemetry-value--danger'}`}>
              {t.external_ai_calls ?? 0}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--color-text-tertiary)', marginTop: 'var(--space-2)' }}>
              Target: 0 (Strict)
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telemetry-label">
              <Wifi size={13} style={{ color: 'var(--color-text-cyan)' }} />
              <span>External Calls</span>
            </div>
            <div className={`telemetry-value ${(t.external_calls || 0) === 0 ? 'telemetry-value--safe' : 'telemetry-value--warn'}`}>
              {t.external_calls ?? 0}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--color-text-tertiary)', marginTop: 'var(--space-2)' }}>
              Network Isolation
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telemetry-label">
              <Ban size={13} style={{ color: 'var(--color-status-failed)' }} />
              <span>Blocked Attempts</span>
            </div>
            <div className={`telemetry-value ${(t.blocked_attempts || 0) > 0 ? 'telemetry-value--danger' : 'telemetry-value--safe'}`}>
              {t.blocked_attempts ?? 0}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--color-text-tertiary)', marginTop: 'var(--space-2)' }}>
              Intercepted by Proxy
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telemetry-label">
              <Server size={13} style={{ color: 'var(--color-accent-primary)' }} />
              <span>Local Model Calls</span>
            </div>
            <div className="telemetry-value telemetry-value--safe">
              {t.local_model_calls ?? 0}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--color-text-tertiary)', marginTop: 'var(--space-2)' }}>
              On-Premise GPUs
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telemetry-label">
              <Database size={13} style={{ color: 'var(--color-text-purple)' }} />
              <span>Local Tool Calls</span>
            </div>
            <div className="telemetry-value telemetry-value--safe">
              {t.local_tool_calls ?? 0}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--color-text-tertiary)', marginTop: 'var(--space-2)' }}>
              Sandboxed Execution
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telemetry-label">
              <Eye size={13} style={{ color: 'var(--color-text-cyan)' }} />
              <span>Local RAG Invocations</span>
            </div>
            <div className="telemetry-value telemetry-value--safe">
              {t.local_rag_calls ?? 0}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--color-text-tertiary)', marginTop: 'var(--space-2)' }}>
              ChromaDB Vector Bus
            </div>
          </div>
        </div>
      </div>

      {/* ── Security Audit Log ── */}
      <div className="section">
        <div className="card-header">
          <span className="card-title">Real-Time Security Audit Log</span>
          <span className="text-xs text-secondary font-medium">{events.length} audit records</span>
        </div>

        {evLoading ? (
          <LoadingState message="Querying audit bus…" />
        ) : evError ? (
          <ErrorState message={evError} onRetry={refetchEv} />
        ) : events.length === 0 ? (
          <EmptyState
            icon={ShieldCheck}
            title="Clean Audit Record"
            message="No security anomalies detected. All agent tool calls and data access have passed sovereign compliance."
          />
        ) : (
          <div className="card" style={{ padding: 0 }}>
            <div className="data-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Event Type</th>
                    <th>Description</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((event, idx) => (
                    <tr key={event.id || idx}>
                      <td className="cell-mono">{formatTimestamp(event.timestamp)}</td>
                      <td>
                        <StatusBadge status={event.type === 'BLOCKED' ? 'DENIED' : event.type || event.severity} />
                      </td>
                      <td style={{ color: 'var(--color-text-primary)' }}>
                        {event.description || event.message || '—'}
                      </td>
                      <td>
                        <span style={{
                          color: event.severity === 'HIGH' || event.severity === 'CRITICAL'
                            ? 'var(--color-status-failed)'
                            : event.severity === 'MEDIUM' ? 'var(--color-status-degraded)'
                            : 'var(--color-text-secondary)',
                          fontWeight: 600,
                          fontSize: 'var(--text-xs)',
                        }}>
                          {event.severity || 'INFO'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
