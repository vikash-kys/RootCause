import { ConfidenceMeter } from './shared';

const STEP_CONFIG = {
  intake: { icon: '📄', label: 'Intake', number: 1 },
  extraction: { icon: '🔍', label: 'Extraction', number: 2 },
  classification: { icon: '🏷️', label: 'Classification', number: 3 },
  summarization: { icon: '📝', label: 'Summarization', number: 4 },
};

function getNodeStatus(span) {
  if (span.error) return 'failure';
  if (span.confidence_score <= 2) return 'degraded';
  return 'success';
}

export default function PipelineGraph({ spans, rootCauseStep, onSelectSpan, selectedSpan }) {
  if (!spans || spans.length === 0) return null;

  return (
    <div className="pipeline-graph">
      {spans.map((span, index) => {
        const config = STEP_CONFIG[span.step_name] || { icon: '?', label: span.step_name, number: index + 1 };
        const status = getNodeStatus(span);
        const isRootCause = rootCauseStep === span.step_name;
        const isSelected = selectedSpan?.span_id === span.span_id;

        return (
          <div key={span.span_id} style={{ display: 'flex', alignItems: 'center' }}>
            {index > 0 && (
              <div className={`pipeline-connector ${status !== 'failure' ? 'animated' : ''}`} />
            )}
            <div
              className={`pipeline-node status-${status} ${isRootCause ? 'root-cause' : ''}`}
              onClick={() => onSelectSpan?.(span)}
              style={{
                outline: isSelected ? '2px solid var(--accent)' : 'none',
                outlineOffset: '8px',
                borderRadius: 'var(--radius-md)',
              }}
            >
              <div className="node-circle">
                {config.icon}
              </div>
              <div className="node-label">{config.label}</div>
              <ConfidenceMeter score={span.confidence_score} />
              <div className="node-sublabel">
                {span.latency_ms?.toFixed(0)}ms
              </div>
              {isRootCause && (
                <span className="badge badge-error" style={{ marginTop: '4px', fontSize: '10px' }}>
                  ROOT CAUSE
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
