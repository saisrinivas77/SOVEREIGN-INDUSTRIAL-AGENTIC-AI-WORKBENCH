import React from 'react';
import { Package, Download, FileText, FileSpreadsheet, FileCode, File, CheckCircle2 } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { fetchArtifacts, getArtifactDownloadUrl, downloadPdfReport } from '../services/api';
import StatusBadge from '../components/shared/StatusBadge';
import EmptyState from '../components/shared/EmptyState';
import ErrorState from '../components/shared/ErrorState';
import LoadingState from '../components/shared/LoadingState';
import { formatTimestamp, formatHash } from '../utils/formatters';

const TYPE_ICONS = {
  DOCX: FileText,
  XLSX: FileSpreadsheet,
  PDF: File,
  CODE: FileCode,
  CALCULATION: FileSpreadsheet,
  TEXT: FileText,
};

/**
 * Royal Blue & White Artifacts page.
 * Displays verified output documents with hashes and download triggers.
 */
export default function ArtifactsPage() {
  const { data, loading, error, refetch } = useApi(fetchArtifacts);

  if (loading) return <LoadingState message="Querying generated business artifacts…" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const artifacts = Array.isArray(data) ? data : data?.artifacts || [];

  if (artifacts.length === 0) {
    return (
      <div className="animate-fade-in">
        <div className="page-header">
          <div>
            <h1 className="page-title">
              <span className="gradient-text">Verified Business Artifacts</span>
            </h1>
            <p className="page-subtitle">AI-generated inspection reports, memos, and audit calculations</p>
          </div>
        </div>
        <EmptyState
          icon={Package}
          title="No Generated Artifacts Yet"
          message="Run an engineering task in the Workbench to produce verified DOCX approval notes, XLSX inspection sheets, or calculation summaries."
        />
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <span className="gradient-text">Verified Business Artifacts</span>
          </h1>
          <p className="page-subtitle">{artifacts.length} verified artifact{artifacts.length !== 1 ? 's' : ''} available</p>
        </div>
      </div>

      <div className="grid-cards">
        {artifacts.map((artifact, idx) => {
          const Icon = TYPE_ICONS[artifact.type] || File;
          const isVerified = artifact.verification_status === 'VERIFIED';

          return (
            <div className="card animate-fade-in" key={artifact.id || idx} style={{ animationDelay: `${idx * 60}ms` }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)', marginBottom: 'var(--space-3)' }}>
                <div style={{
                  width: 44,
                  height: 44,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: 'var(--radius-md)',
                  background: isVerified ? 'var(--color-status-healthy-bg)' : 'var(--color-accent-light)',
                  color: isVerified ? 'var(--color-status-healthy)' : 'var(--color-accent-primary)',
                  flexShrink: 0,
                }}>
                  <Icon size={22} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, color: 'var(--color-text-primary)', wordBreak: 'break-word' }}>
                    {artifact.filename}
                  </div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-accent-primary)', fontWeight: 600, marginTop: 2 }}>
                    {artifact.type}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', fontSize: 'var(--text-xs)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-text-tertiary)' }}>Created</span>
                  <span style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{formatTimestamp(artifact.created_at)}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--color-text-tertiary)' }}>Verification</span>
                  <StatusBadge status={artifact.verification_status} />
                </div>

                {artifact.hash && (
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-tertiary)' }}>SHA-256 Hash</span>
                    <span className="mono" style={{ fontSize: 'var(--text-xs)', color: 'var(--color-accent-primary)', fontWeight: 600 }}>
                      {formatHash(artifact.hash)}
                    </span>
                  </div>
                )}
              </div>

              {(artifact.id || artifact.artifact_id) && (
                <div style={{ marginTop: 'var(--space-4)', paddingTop: 'var(--space-3)', borderTop: '1px solid var(--color-border-subtle)', display: 'flex', gap: 'var(--space-2)' }}>
                  <a
                    href={getArtifactDownloadUrl(artifact.id || artifact.artifact_id)}
                    className="btn btn-secondary btn-sm"
                    style={{ flex: 1, justifyContent: 'center', textDecoration: 'none' }}
                    download={artifact.filename}
                  >
                    <Download size={13} />
                    <span>Download {artifact.type || 'File'}</span>
                  </a>

                  <button
                    className="btn btn-primary btn-sm"
                    style={{ justifyContent: 'center' }}
                    onClick={() => downloadPdfReport('task', artifact.task_id || null, artifact.filename)}
                    title="Export Analysis Report in PDF format"
                  >
                    <Download size={13} />
                    <span>PDF</span>
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

