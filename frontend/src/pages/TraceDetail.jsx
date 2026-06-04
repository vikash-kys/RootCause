import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getTrace, flagTrace, getDiagnosis, confirmDiagnosis } from '../api';
import { StatusBadge, LoadingSpinner, FailureTypeBadge } from '../components/shared';
import PipelineGraph from '../components/PipelineGraph';
import SpanDetail from '../components/SpanDetail';

export default function TraceDetail() {
  const { traceId } = useParams();
  const navigate = useNavigate();
  const [trace, setTrace] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [selectedSpan, setSelectedSpan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [diagnosing, setDiagnosing] = useState(false);
  const [flagging, setFlagging] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchTrace();
  }, [traceId]);

  const fetchTrace = async () => {
    try {
      const data = await getTrace(traceId);
      setTrace(data);
    } catch (err) {
      console.error('Failed to fetch trace:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFlag = async () => {
    setFlagging(true);
    try {
      const result = await flagTrace(traceId, 'Bad output flagged by user');
      setDiagnosis(result.diagnosis);
      setTrace(prev => ({ ...prev, flagged: true }));
      showToast('Trace flagged and diagnosis generated', 'success');
    } catch (err) {
      showToast('Failed to flag trace', 'error');
    } finally {
      setFlagging(false);
    }
  };

  const handleDiagnose = async () => {
    setDiagnosing(true);
    try {
      const data = await getDiagnosis(traceId);
      setDiagnosis(data);
    } catch (err) {
      showToast('Failed to run diagnosis', 'error');
    } finally {
      setDiagnosing(false);
    }
  };

  const handleConfirm = async () => {
    setConfirming(true);
    try {
      await confirmDiagnosis(traceId);
      showToast('Eval case created! The evaluation dataset has grown.', 'success');
    } catch (err) {
      showToast('Failed to confirm diagnosis', 'error');
    } finally {
      setConfirming(false);
    }
  };

  const showToast = (message, type) => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  if (loading) return <LoadingSpinner message="Loading trace..." />;
  if (!trace) return <div className="empty-state"><h3>Trace not found</h3></div>;

  const rootCauseStep = diagnosis?.root_cause_step;

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <button className="btn btn-secondary btn-sm" onClick={() => navigate('/traces')}>
                ← Back
              </button>
              <h2 style={{ margin: 0 }}>Trace Detail</h2>
              <StatusBadge status={trace.status} />
              {trace.flagged && <span title="Flagged">🚩</span>}
            </div>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-muted)' }}>
              {trace.trace_id}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className="btn btn-secondary"
              onClick={handleDiagnose}
              disabled={diagnosing}
            >
              {diagnosing ? '⟳ Analyzing...' : '🔍 Diagnose'}
            </button>
            {!trace.flagged && (
              <button
                className="btn btn-danger"
                onClick={handleFlag}
                disabled={flagging}
              >
                {flagging ? '⟳ Flagging...' : '🚩 Flag as Bad'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Trace Meta */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-label">Status</div>
          <div style={{ marginTop: '8px' }}><StatusBadge status={trace.status} /></div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Final Score</div>
          <div className="stat-value">{(trace.final_score || 0).toFixed(1)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Steps</div>
          <div className="stat-value">{trace.spans?.length || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Failure Type</div>
          <div style={{ marginTop: '8px' }}>
            <FailureTypeBadge type={trace.failure_type} />
            {(!trace.failure_type || trace.failure_type === 'none') && (
              <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>None</span>
            )}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Created</div>
          <div style={{ fontSize: '14px', fontFamily: 'var(--font-mono)', marginTop: '8px' }}>
            {new Date(trace.created_at).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Pipeline Visualization */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <h3 className="card-title">Pipeline Flow</h3>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Click a node to inspect</span>
        </div>
        <PipelineGraph
          spans={trace.spans || []}
          rootCauseStep={rootCauseStep}
          onSelectSpan={setSelectedSpan}
          selectedSpan={selectedSpan}
        />
      </div>

      {/* Diagnosis / Evidence Chain */}
      {diagnosis && (
        <div className="evidence-chain" style={{ marginBottom: '24px' }}>
          <h3>🔬 Root Cause Analysis</h3>
          <div style={{ marginBottom: '16px' }}>
            <p style={{ fontSize: '14px', color: 'var(--text-primary)', fontWeight: 500 }}>
              {diagnosis.summary}
            </p>
          </div>

          {/* Step Diagnoses */}
          {diagnosis.step_diagnoses && diagnosis.step_diagnoses.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '12px' }}>
                Step-by-Step Quality Scores
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                {diagnosis.step_diagnoses.map((sd, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '12px',
                      borderRadius: 'var(--radius-md)',
                      background: sd.is_root_cause ? 'var(--error-bg)' : 'var(--bg-glass)',
                      border: `1px solid ${sd.is_root_cause ? 'var(--error-border)' : 'var(--border-primary)'}`,
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 600, fontSize: '13px' }}>
                        {sd.step_name?.charAt(0).toUpperCase() + sd.step_name?.slice(1)}
                      </span>
                      {sd.is_root_cause && <span className="badge badge-error" style={{ fontSize: '10px' }}>ROOT CAUSE</span>}
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '20px', fontWeight: 700, color: sd.quality_score < 0.5 ? 'var(--error)' : sd.quality_score < 0.7 ? 'var(--warning)' : 'var(--success)' }}>
                      {(sd.quality_score * 100).toFixed(0)}%
                    </div>
                    {sd.explanation && (
                      <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                        {sd.explanation}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Evidence Chain Text */}
          {diagnosis.evidence_chain && (
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Evidence Chain
              </h4>
              <div className="evidence-text" dangerouslySetInnerHTML={{
                __html: diagnosis.evidence_chain
                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/\n/g, '<br />')
              }} />
            </div>
          )}

          {/* Confirm button */}
          <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
            <button
              className="btn btn-success"
              onClick={handleConfirm}
              disabled={confirming}
            >
              {confirming ? '⟳ Creating eval case...' : '✓ Confirm & Create Eval Case'}
            </button>
          </div>
        </div>
      )}

      {/* Selected Span Detail */}
      {selectedSpan && (
        <SpanDetail span={selectedSpan} onClose={() => setSelectedSpan(null)} />
      )}

      {/* Input Document */}
      {trace.input_document && (
        <div className="card" style={{ marginTop: '24px' }}>
          <div className="card-header">
            <h3 className="card-title">Input Document</h3>
            <span className="badge badge-info">{trace.input_document.source || 'manual'}</span>
          </div>
          <div className="code-block" style={{ maxHeight: '300px' }}>
            {trace.input_document.content}
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === 'success' ? '✓' : '✕'} {toast.message}
        </div>
      )}
    </div>
  );
}
