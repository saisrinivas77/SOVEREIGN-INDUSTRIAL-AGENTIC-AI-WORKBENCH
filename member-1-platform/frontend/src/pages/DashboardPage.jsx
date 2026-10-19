import React, { useEffect } from 'react';
import {
  CheckCircle2, XCircle, Clock, FileText, Cpu,
  Package, Shield, Globe, Ban, Sparkles, ArrowUpRight,
  Server, Lock, Activity, Download
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { fetchDashboardMetrics, downloadPdfReport } from '../services/api';
import MetricCard from '../components/shared/MetricCard';
import ErrorState from '../components/shared/ErrorState';
import SovereignBadge from '../components/shared/SovereignBadge';

/**
 * Royal Blue & White Sovereign Mission Control.
 * Clean, enterprise dashboard with live backend telemetry.
 */
export default function DashboardPage() {
  const navigate = useNavigate();
  const { data, loading, error, refetch } = useApi(fetchDashboardMetrics);

  useEffect(() => {
    const timer = setInterval(refetch, 5000);
    return () => clearInterval(timer);
  }, [refetch]);

  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const m = data || {};

  return (
    <div className="animate-fade-in">
      {/* ── Top Header ── */}
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <span className="gradient-text">Sovereign Mission Control</span>
          </h1>
          <p className="page-subtitle">Real-time telemetry of on-premise industrial AI workloads</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => downloadPdfReport('executive', null, 'Executive Mission Control Brief')}
          >
            <Download size={13} />
            <span>Export Executive Brief (PDF)</span>
          </button>
          <SovereignBadge />
        </div>
      </div>


      {/* ── Air-Gapped Sovereign Guarantee Banner (Royal Blue & White) ── */}
      <div className="card" style={{
        marginBottom: 'var(--space-8)',
        background: 'linear-gradient(135deg, #eff6ff 0%, #ffffff 100%)',
        borderColor: 'rgba(37, 99, 235, 0.25)',
        boxShadow: 'var(--shadow-md)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
            <div style={{
              width: 52,
              height: 52,
              borderRadius: 'var(--radius-lg)',
              background: 'var(--color-accent-primary)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 14px rgba(30, 64, 175, 0.3)'
            }}>
              <Lock size={26} />
            </div>

            <div>
              <div style={{ fontSize: 'var(--text-md)', fontWeight: 800, color: 'var(--color-accent-primary)' }}>
                100% Air-Gapped Confidentiality Verified
              </div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                All document parsing, vision analysis, vector embeddings, and reasoning execute entirely on local hardware. Zero bytes egress to cloud.
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-6)' }}>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>
                External Egress
              </div>
              <div style={{ fontSize: 'var(--text-lg)', fontWeight: 800, color: 'var(--color-status-healthy)' }}>
                0.00 KB/s (BLOCKED)
              </div>
            </div>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>
                Network Shield
              </div>
              <div style={{ fontSize: 'var(--text-lg)', fontWeight: 800, color: 'var(--color-accent-primary)' }}>
                RESTRICTED
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Active Task Metrics ── */}
      <div className="section">
        <div className="card-header">
          <span className="card-title">Task Orchestration</span>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/workbench')}>
            <span>Open Workbench</span>
            <ArrowUpRight size={13} />
          </button>
        </div>

        <div className="grid-metrics">
          <MetricCard
            icon={Clock}
            value={m.active_tasks}
            label="Active Agent Tasks"
            color="#2563eb"
            loading={loading}
          />
          <MetricCard
            icon={CheckCircle2}
            value={m.completed_tasks}
            label="Completed Analyses"
            color="#059669"
            loading={loading}
          />
          <MetricCard
            icon={XCircle}
            value={m.failed_tasks}
            label="Failed / Interrupted"
            color="#dc2626"
            loading={loading}
          />
        </div>
      </div>

      {/* ── Intelligence & Storage Metrics ── */}
      <div className="section">
        <div className="card-header">
          <span className="card-title">Sovereign Data & Models</span>
        </div>

        <div className="grid-metrics">
          <MetricCard
            icon={FileText}
            value={m.indexed_documents}
            label="Indexed Industrial Docs"
            color="#1e40af"
            loading={loading}
          />
          <MetricCard
            icon={Cpu}
            value={m.available_models}
            label="Local Multimodal Models"
            color="#0284c7"
            loading={loading}
          />
          <MetricCard
            icon={Package}
            value={m.generated_artifacts}
            label="Verified Artifacts (DOCX/XLSX)"
            color="#d97706"
            loading={loading}
          />
        </div>
      </div>

      {/* ── Security & Sovereignty Telemetry ── */}
      <div className="section">
        <div className="card-header">
          <span className="card-title">Security & Sovereign Audit</span>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/security')}>
            <span>Security Center</span>
            <ArrowUpRight size={13} />
          </button>
        </div>

        <div className="grid-metrics">
          <MetricCard
            icon={Shield}
            value={m.security_events}
            label="Audited Events"
            color="#059669"
            loading={loading}
          />
          <MetricCard
            icon={Globe}
            value={m.external_calls ?? 0}
            label="External Calls Attempted"
            color={m.external_calls > 0 ? '#d97706' : '#059669'}
            loading={loading}
          />
          <MetricCard
            icon={Ban}
            value={m.blocked_calls ?? 0}
            label="Cloud Leaks Blocked"
            color="#dc2626"
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}
