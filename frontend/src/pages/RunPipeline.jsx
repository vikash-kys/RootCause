import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { runPipeline } from '../api';
import { StatusBadge, LoadingSpinner } from '../components/shared';

const SAMPLE_DOCS = [
  {
    label: 'Consulting Agreement',
    content: `CONSULTING SERVICES AGREEMENT\n\nThis Agreement is entered into as of June 1, 2025, by Acme Corp ("Company") and Jane Doe ("Consultant").\n\n1. SCOPE: The Consultant shall provide AI/ML strategy advisory services.\n2. COMPENSATION: $50,000 fixed fee, payable in two installments.\n3. TERM: June 1 through August 31, 2025.\n4. CONFIDENTIALITY: Standard NDA terms apply.\n\nSigned:\nAcme Corp          Jane Doe\nDate: June 1, 2025`,
  },
  {
    label: 'Invoice (Mixed Currency)',
    content: `INVOICE #2025-0099\n\nFrom: GlobalServices AG, Zurich\nTo: Pacific Trading Co, Singapore\n\nTranslation Services:\n- Japanese to English: ¥500,000\n- German to English: €3,200\n- French to Spanish: €1,500\n\nConsulting: $4,000 USD\nLocal fee: SGD 800\n\nTotal (estimated USD): $12,500\nPayment: Net 30`,
  },
  {
    label: 'Ambiguous Document',
    content: `Hi Team,\n\nJust wanted to confirm our agreement on the project terms. We'll deliver the analytics dashboard by end of Q3 for $85,000. Payment in three milestones. If either side wants out, 2 weeks notice.\n\nReply "confirmed" and we're good to go.\n\nBest,\nAlex`,
  },
  {
    label: 'Sparse Document',
    content: `NDA. Parties keep info secret. 2 years. NY law.`,
  },
];

export default function RunPipeline() {
  const [content, setContent] = useState('');
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleRun = async () => {
    if (!content.trim()) return;
    setRunning(true);
    setResult(null);
    setError(null);
    try {
      const data = await runPipeline(content);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  const loadSample = (sample) => {
    setContent(sample.content);
    setResult(null);
    setError(null);
  };

  return (
    <div>
      <div className="page-header">
        <h2>Run Pipeline</h2>
        <p>Process a document through the 4-step AI pipeline and inspect the trace</p>
      </div>

      {/* Sample Documents */}
      <div style={{ marginBottom: '16px' }}>
        <span style={{ fontSize: '13px', color: 'var(--text-muted)', marginRight: '12px' }}>Quick load:</span>
        {SAMPLE_DOCS.map((sample, i) => (
          <button
            key={i}
            className="btn btn-secondary btn-sm"
            style={{ marginRight: '8px', marginBottom: '8px' }}
            onClick={() => loadSample(sample)}
          >
            {sample.label}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="form-group">
          <label>Document Content</label>
          <textarea
            className="input"
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="Paste or type a document here... (contract, invoice, report, or correspondence)"
            style={{ minHeight: '250px' }}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {content.length} characters | {content.split(/\s+/).filter(Boolean).length} words
          </span>
          <button
            className="btn btn-primary btn-lg"
            onClick={handleRun}
            disabled={running || !content.trim()}
          >
            {running ? '⟳ Processing...' : '▷ Run Pipeline'}
          </button>
        </div>
      </div>

      {/* Loading */}
      {running && <LoadingSpinner message="Running 4-step pipeline..." />}

      {/* Error */}
      {error && (
        <div className="card" style={{ borderColor: 'var(--error-border)', marginBottom: '24px' }}>
          <h3 style={{ color: 'var(--error)', marginBottom: '8px' }}>Error</h3>
          <p style={{ color: 'var(--text-secondary)' }}>{error}</p>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="card" style={{ borderColor: result.status === 'success' ? 'var(--success-border)' : result.status === 'degraded' ? 'var(--warning-border)' : 'var(--error-border)' }}>
          <div className="card-header">
            <h3 className="card-title">Pipeline Result</h3>
            <StatusBadge status={result.status} />
          </div>

          <div className="stats-grid" style={{ marginBottom: '16px' }}>
            <div className="span-meta-item">
              <label>Trace ID</label>
              <div className="value">{result.trace_id?.slice(0, 12)}...</div>
            </div>
            <div className="span-meta-item">
              <label>Steps</label>
              <div className="value">{result.spans?.length || 0}</div>
            </div>
            <div className="span-meta-item">
              <label>Final Score</label>
              <div className="value">{(result.final_score || 0).toFixed(1)}</div>
            </div>
          </div>

          {/* Summary Output */}
          {result.final_output?.summary && (
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '13px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Generated Summary
              </h4>
              <div className="code-block">
                {JSON.stringify(result.final_output.summary, null, 2)}
              </div>
            </div>
          )}

          {/* Classification */}
          {result.final_output?.classification && (
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '13px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Classification
              </h4>
              <span className="badge badge-info">
                {result.final_output.classification.document_type}
              </span>
              <span style={{ marginLeft: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
                Confidence: {result.final_output.classification.classification_confidence}/5
              </span>
            </div>
          )}

          <button
            className="btn btn-primary"
            onClick={() => navigate(`/traces/${result.trace_id}`)}
          >
            View Full Trace →
          </button>
        </div>
      )}
    </div>
  );
}
