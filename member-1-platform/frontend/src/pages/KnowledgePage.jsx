import React, { useState } from 'react';
import { Search, BookOpen, Download } from 'lucide-react';
import { searchKnowledge, downloadPdfReport } from '../services/api';
import EmptyState from '../components/shared/EmptyState';
import ErrorState from '../components/shared/ErrorState';
import LoadingState from '../components/shared/LoadingState';
import { formatScore } from '../utils/formatters';

/**
 * Royal Blue & White Knowledge Base page.
 * Clean RAG vector search with source citations.
 */
export default function KnowledgePage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      const data = await searchKnowledge(query.trim());
      setResults(Array.isArray(data) ? data : data?.results || data?.chunks || []);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <span className="gradient-text">Knowledge Base & RAG Retrieval</span>
          </h1>
          <p className="page-subtitle">Search indexed industrial standard documents with verifiable citations</p>
        </div>
        {searched && results && results.length > 0 && (
          <button
            className="btn btn-primary btn-sm"
            onClick={() => downloadPdfReport('document', null, `RAG Retrieval Report: ${query}`)}
          >
            <Download size={13} />
            <span>Export RAG Report (PDF)</span>
          </button>
        )}
      </div>


      {/* Search Bar */}
      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={16} style={{
              position: 'absolute',
              left: 'var(--space-4)',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--color-accent-primary)',
            }} />
            <input
              type="text"
              placeholder="Search standards & technical reports… (e.g. 'ASME Section VIII Div 1 weld defect acceptance criteria')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ paddingLeft: 'var(--space-10)' }}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading || !query.trim()}>
            {loading ? 'Searching…' : 'Search RAG'}
          </button>
        </form>
      </div>

      {/* Results View */}
      {loading && <LoadingState message="Querying local vector embeddings in ChromaDB…" />}

      {error && <ErrorState message={error} onRetry={() => handleSearch({ preventDefault: () => {} })} />}

      {!loading && !error && searched && results && results.length === 0 && (
        <EmptyState
          icon={BookOpen}
          title="No Passages Found"
          message="No matching document chunks found. Verify that technical documents have been ingested and indexed."
        />
      )}

      {!loading && !error && results && results.length > 0 && (
        <div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-accent-primary)', fontWeight: 700, marginBottom: 'var(--space-3)' }}>
            {results.length} RELEVANT CHUNKS RETRIEVED
          </div>

          {results.map((result, idx) => (
            <div className="card animate-fade-in" key={result.chunk_id || idx} style={{ marginBottom: 'var(--space-4)', animationDelay: `${idx * 60}ms` }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
                <span style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--color-accent-primary)' }}>
                  {result.document || result.filename || 'Technical Document'}
                </span>
                <span style={{
                  fontSize: 'var(--text-xs)',
                  fontWeight: 800,
                  color: 'var(--color-status-healthy)',
                  background: 'var(--color-status-healthy-bg)',
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-full)'
                }}>
                  {formatScore(result.relevance_score || result.score)} Match
                </span>
              </div>

              <div style={{ display: 'flex', gap: 'var(--space-4)', fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)', marginBottom: 'var(--space-3)' }}>
                {result.page != null && <span>Page: <strong>{result.page}</strong></span>}
                {result.section && <span>Section: <strong>{result.section}</strong></span>}
                {result.chunk != null && <span>Chunk: <strong>#{result.chunk}</strong></span>}
              </div>

              {(result.excerpt || result.content || result.text) && (
                <div style={{
                  fontSize: 'var(--text-sm)',
                  color: 'var(--color-text-secondary)',
                  lineHeight: 1.6,
                  background: '#f8fafc',
                  borderLeft: '3px solid var(--color-accent-primary)',
                  padding: 'var(--space-3) var(--space-4)',
                  borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
                }}>
                  {result.excerpt || result.content || result.text}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {!searched && !loading && (
        <EmptyState
          icon={BookOpen}
          title="Search the Industrial Knowledge Base"
          message="Enter an engineering inquiry above to retrieve verified passages with page and section citations from local ChromaDB."
        />
      )}
    </div>
  );
}
