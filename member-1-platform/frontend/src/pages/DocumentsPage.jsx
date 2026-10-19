import React, { useState } from 'react';
import { Upload, FileText, Download } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { fetchDocuments, uploadDocuments, downloadPdfReport } from '../services/api';

import DataTable from '../components/shared/DataTable';
import StatusBadge from '../components/shared/StatusBadge';
import FileUpload from '../components/shared/FileUpload';
import { formatFileSize } from '../utils/formatters';

/**
 * Royal Blue & White Documents page.
 * Document ingestion table with OCR & indexing status.
 */
export default function DocumentsPage() {
  const { data, loading, error, refetch } = useApi(fetchDocuments);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [files, setFiles] = useState([]);

  const handleUpload = async () => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setUploadError(null);
    try {
      await uploadDocuments(files);
      setFiles([]);
      setShowUpload(false);
      refetch();
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const documents = Array.isArray(data) ? data : data?.documents || [];

  const columns = [
    {
      key: 'filename',
      label: 'Document Name',
      render: (row) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <FileText size={16} style={{ color: 'var(--color-accent-primary)', flexShrink: 0 }} />
          <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{row.filename}</span>
        </div>
      ),
    },
    { key: 'document_id', label: 'Document ID', mono: true },
    { key: 'type', label: 'Format' },
    {
      key: 'size',
      label: 'File Size',
      render: (row) => <span className="mono">{formatFileSize(row.size)}</span>,
    },
    {
      key: 'processing_status',
      label: 'Pipeline Status',
      render: (row) => <StatusBadge status={row.processing_status} />,
    },
    {
      key: 'ocr_status',
      label: 'OCR Engine',
      render: (row) => <StatusBadge status={row.ocr_status} />,
    },
    {
      key: 'index_status',
      label: 'ChromaDB Index',
      render: (row) => <StatusBadge status={row.index_status} />,
    },
  ];

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <span className="gradient-text">Confidential Document Vault</span>
          </h1>
          <p className="page-subtitle">Uploaded industrial drawings, PDFs, and sensor telemetry tables</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <button
            className="btn btn-secondary"
            onClick={() => downloadPdfReport('document', null, 'Confidential Document Vault Audit')}
          >
            <Download size={14} />
            <span>Document Audit (PDF)</span>
          </button>
          <button className="btn btn-primary" onClick={() => setShowUpload(!showUpload)}>
            <Upload size={15} />
            <span>Upload Documents</span>
          </button>
        </div>
      </div>


      {showUpload && (
        <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
          <FileUpload files={files} onFilesChange={setFiles} />
          {uploadError && (
            <div style={{
              marginTop: 'var(--space-3)',
              padding: 'var(--space-2) var(--space-3)',
              background: 'var(--color-status-failed-bg)',
              color: 'var(--color-status-failed)',
              borderRadius: 'var(--radius-sm)',
              fontSize: 'var(--text-sm)',
            }}>
              {uploadError}
            </div>
          )}
          <div style={{ marginTop: 'var(--space-4)', display: 'flex', gap: 'var(--space-3)' }}>
            <button
              className="btn btn-primary"
              disabled={uploading || !files?.length}
              onClick={handleUpload}
            >
              {uploading ? 'Ingesting…' : 'Start Secure Upload'}
            </button>
            <button className="btn btn-secondary" onClick={() => { setShowUpload(false); setFiles([]); }}>
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <DataTable
          columns={columns}
          data={documents}
          loading={loading}
          error={error}
          emptyMessage="No documents in vault. Click 'Upload Documents' above to ingest confidential engineering files."
          onRetry={refetch}
        />
      </div>
    </div>
  );
}
