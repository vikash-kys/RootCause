export function StatusBadge({ status }) {
  const config = {
    success: { className: 'badge-success', label: 'Success', icon: '✓' },
    degraded: { className: 'badge-warning', label: 'Degraded', icon: '⚠' },
    failure: { className: 'badge-error', label: 'Failure', icon: '✕' },
    running: { className: 'badge-info', label: 'Running', icon: '↻' },
  };

  const c = config[status] || config.failure;

  return (
    <span className={`badge ${c.className}`}>
      <span className="badge-dot"></span>
      {c.label}
    </span>
  );
}

export function ConfidenceMeter({ score, max = 5 }) {
  const level = score <= 2 ? 'low' : score <= 3 ? 'medium' : '';

  return (
    <div className="confidence-meter" title={`Confidence: ${score}/${max}`}>
      {Array.from({ length: max }, (_, i) => (
        <div
          key={i}
          className={`meter-bar ${i < score ? `filled ${level}` : ''}`}
        />
      ))}
      <span style={{ marginLeft: '6px', fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
        {score}/{max}
      </span>
    </div>
  );
}

export function FailureTypeBadge({ type }) {
  const labels = {
    extraction_hallucination: 'Hallucination',
    misclassification: 'Misclassification',
    propagation_error: 'Propagation',
    prompt_failure: 'Prompt Failure',
    context_loss: 'Context Loss',
    none: 'None',
  };

  if (!type || type === 'none') return null;

  return (
    <span className="badge badge-error" style={{ fontSize: '11px' }}>
      {labels[type] || type}
    </span>
  );
}

export function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="loading">
      <div className="spinner"></div>
      <div className="loading-text">{message}</div>
    </div>
  );
}

export function EmptyState({ icon = '📭', title, message, action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{message}</p>
      {action && <div style={{ marginTop: '16px' }}>{action}</div>}
    </div>
  );
}
