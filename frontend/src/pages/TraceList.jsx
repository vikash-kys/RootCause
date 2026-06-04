import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { listTraces } from '../api';
import { StatusBadge, LoadingSpinner, FailureTypeBadge, EmptyState } from '../components/shared';

export default function TraceList() {
  const [traces, setTraces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ status: '', flagged: '' });
  const navigate = useNavigate();

  const fetchTraces = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter.status) params.status = filter.status;
      if (filter.flagged === 'true') params.flagged = true;
      if (filter.flagged === 'false') params.flagged = false;
      const data = await listTraces(params);
      setTraces(data.traces || []);
    } catch (err) {
      console.error('Failed to fetch traces:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTraces(); }, [filter]);

  const statusFilters = ['', 'success', 'degraded', 'failure'];

  return (
    <div>
      <div className="page-header">
        <h2>Pipeline Traces</h2>
        <p>Browse and inspect all pipeline execution traces</p>
      </div>

      {/* Filters */}
      <div className="filter-bar">
        <span style={{ fontSize: '13px', color: 'var(--text-muted)', fontWeight: 500 }}>Status:</span>
        {statusFilters.map(s => (
          <button
            key={s || 'all'}
            className={`filter-chip ${filter.status === s ? 'active' : ''}`}
            onClick={() => setFilter(prev => ({ ...prev, status: s }))}
          >
            {s || 'All'}
          </button>
        ))}

        <span style={{ fontSize: '13px', color: 'var(--text-muted)', fontWeight: 500, marginLeft: '16px' }}>Flagged:</span>
        {['', 'true', 'false'].map(f => (
          <button
            key={f || 'any'}
            className={`filter-chip ${filter.flagged === f ? 'active' : ''}`}
            onClick={() => setFilter(prev => ({ ...prev, flagged: f }))}
          >
            {f === '' ? 'Any' : f === 'true' ? '🚩 Yes' : 'No'}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner message="Loading traces..." />
      ) : traces.length === 0 ? (
        <EmptyState
          icon="📭"
          title="No traces found"
          message="Run the pipeline on some documents to see traces here."
          action={<button className="btn btn-primary" onClick={() => navigate('/run')}>Run Pipeline</button>}
        />
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Trace ID</th>
                <th>Status</th>
                <th>Failure Type</th>
                <th>Steps</th>
                <th>Avg Confidence</th>
                <th>Total Latency</th>
                <th>Input Preview</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {traces.map(trace => (
                <tr
                  key={trace.trace_id}
                  onClick={() => navigate(`/traces/${trace.trace_id}`)}
                  style={{ cursor: 'pointer' }}
                >
                  <td>
                    <code style={{ fontSize: '12px', color: 'var(--accent)' }}>
                      {trace.trace_id?.slice(0, 12)}...
                    </code>
                  </td>
                  <td><StatusBadge status={trace.status} /></td>
                  <td><FailureTypeBadge type={trace.failure_type} /></td>
                  <td>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px' }}>
                      {trace.step_count || 0}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '13px',
                      color: (trace.avg_confidence || 0) <= 2 ? 'var(--error)' :
                             (trace.avg_confidence || 0) <= 3 ? 'var(--warning)' : 'var(--success)',
                    }}>
                      {(trace.avg_confidence || 0).toFixed(1)}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px' }}>
                      {(trace.total_latency_ms || 0).toFixed(0)}ms
                    </span>
                  </td>
                  <td style={{ maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '13px', color: 'var(--text-muted)' }}>
                    {trace.input_preview || '—'}
                  </td>
                  <td style={{ fontSize: '12px', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                    {new Date(trace.created_at).toLocaleString()}
                  </td>
                  <td>
                    {trace.flagged ? '🚩' : ''}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
