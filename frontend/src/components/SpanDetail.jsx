import { ConfidenceMeter, StatusBadge } from './shared';

export default function SpanDetail({ span, onClose }) {
  if (!span) return null;

  const formatJson = (data) => {
    try {
      return JSON.stringify(data, null, 2);
    } catch {
      return String(data);
    }
  };

  return (
    <div className="span-detail">
      <div className="span-detail-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600 }}>
            Step: {span.step_name?.charAt(0).toUpperCase() + span.step_name?.slice(1)}
          </h3>
          <StatusBadge status={span.error ? 'failure' : span.confidence_score <= 2 ? 'degraded' : 'success'} />
        </div>
        {onClose && (
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕ Close</button>
        )}
      </div>

      <div className="span-detail-body">
        <div className="span-meta-grid">
          <div className="span-meta-item">
            <label>Span ID</label>
            <div className="value">{span.span_id?.slice(0, 8)}...</div>
          </div>
          <div className="span-meta-item">
            <label>Latency</label>
            <div className="value">{span.latency_ms?.toFixed(1)}ms</div>
          </div>
          <div className="span-meta-item">
            <label>Tokens</label>
            <div className="value">{span.token_count || 0}</div>
          </div>
          <div className="span-meta-item">
            <label>Confidence</label>
            <ConfidenceMeter score={span.confidence_score} />
          </div>
          <div className="span-meta-item">
            <label>Status</label>
            <div className="value">{span.error ? 'Error' : 'OK'}</div>
          </div>
          <div className="span-meta-item">
            <label>Started</label>
            <div className="value">{new Date(span.started_at).toLocaleTimeString()}</div>
          </div>
        </div>

        {span.error && (
          <div style={{ marginBottom: '16px' }}>
            <label style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--error)', display: 'block', marginBottom: '8px' }}>
              Error
            </label>
            <div className="code-block" style={{ borderColor: 'var(--error-border)' }}>
              {span.error}
            </div>
          </div>
        )}

        <div className="diff-container" style={{ marginBottom: '16px' }}>
          <div className="diff-panel">
            <div className="diff-panel-header input">⬇ Input</div>
            <div className="diff-panel-body">
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {formatJson(span.input_data)}
              </pre>
            </div>
          </div>
          <div className="diff-panel">
            <div className="diff-panel-header output">⬆ Output</div>
            <div className="diff-panel-body">
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {formatJson(span.output_data)}
              </pre>
            </div>
          </div>
        </div>

        {span.prompt_sent && (
          <div style={{ marginBottom: '16px' }}>
            <label style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
              LLM Prompt
            </label>
            <div className="code-block">{span.prompt_sent}</div>
          </div>
        )}

        {span.llm_raw_response && (
          <div>
            <label style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
              LLM Raw Response
            </label>
            <div className="code-block">{span.llm_raw_response}</div>
          </div>
        )}
      </div>
    </div>
  );
}
