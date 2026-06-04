import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAnalytics, listTraces, runDemo } from '../api';
import { StatusBadge, LoadingSpinner, FailureTypeBadge } from '../components/shared';

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [recentTraces, setRecentTraces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoResult, setDemoResult] = useState(null);
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      const [analyticsData, tracesData] = await Promise.all([
        getAnalytics(),
        listTraces({ limit: 10 }),
      ]);
      setAnalytics(analyticsData);
      setRecentTraces(tracesData.traces || []);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleRunDemo = async () => {
    setDemoRunning(true);
    setDemoResult(null);
    try {
      const result = await runDemo();
      setDemoResult(result);
      await fetchData();
    } catch (err) {
      console.error('Demo run failed:', err);
    } finally {
      setDemoRunning(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading dashboard..." />;

  const stats = analytics || {};

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2>Dashboard</h2>
            <p>AI Pipeline Observability — trace, diagnose, and learn from failures</p>
          </div>
          <button
            className="btn btn-primary btn-lg"
            onClick={handleRunDemo}
            disabled={demoRunning}
          >
            {demoRunning ? '⟳ Processing 50 docs...' : '▷ Run Demo (50 docs)'}
          </button>
        </div>
      </div>

      {demoResult && (
        <div className="card" style={{ marginBottom: '24px', borderColor: 'var(--success-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ fontSize: '24px' }}>✓</span>
            <div>
              <strong>Demo Complete!</strong> Processed {demoResult.total} documents:
              <span style={{ color: 'var(--success)', marginLeft: '8px' }}>{demoResult.success} success</span>
              <span style={{ color: 'var(--warning)', marginLeft: '8px' }}>{demoResult.degraded} degraded</span>
              <span style={{ color: 'var(--error)', marginLeft: '8px' }}>{demoResult.failure} failed</span>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">⊡</div>
          <div className="stat-value">{stats.total_traces || 0}</div>
          <div className="stat-label">Total Traces</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ color: 'var(--success)' }}>✓</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.success_count || 0}</div>
          <div className="stat-label">Successful</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ color: 'var(--warning)' }}>⚠</div>
          <div className="stat-value" style={{ color: 'var(--warning)' }}>{stats.degraded_count || 0}</div>
          <div className="stat-label">Degraded</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ color: 'var(--error)' }}>✕</div>
          <div className="stat-value" style={{ color: 'var(--error)' }}>{stats.failure_count || 0}</div>
          <div className="stat-label">Failed</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">◎</div>
          <div className="stat-value">{((stats.failure_rate || 0) * 100).toFixed(1)}%</div>
          <div className="stat-label">Failure Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏱</div>
          <div className="stat-value">{(stats.avg_latency_ms || 0).toFixed(0)}<span style={{ fontSize: '14px', fontWeight: 400 }}>ms</span></div>
          <div className="stat-label">Avg Latency</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✓</div>
          <div className="stat-value">{stats.eval_dataset_size || 0}</div>
          <div className="stat-label">Eval Cases</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ color: 'var(--accent)' }}>↻</div>
          <div className="stat-value" style={{ color: 'var(--accent)' }}>{stats.resolved_issues || 0}</div>
          <div className="stat-label">Resolved Issues</div>
        </div>
      </div>

      {/* Failure Type Breakdown */}
      {stats.failure_by_type && Object.keys(stats.failure_by_type).length > 0 && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-header">
            <h3 className="card-title">Failure Types</h3>
          </div>
          <div className="bar-chart" style={{ height: '150px', paddingBottom: '32px' }}>
            {Object.entries(stats.failure_by_type).map(([type, count]) => {
              const maxCount = Math.max(...Object.values(stats.failure_by_type));
              const height = maxCount > 0 ? (count / maxCount) * 100 : 0;
              return (
                <div
                  key={type}
                  className="bar"
                  style={{
                    height: `${height}%`,
                    background: 'linear-gradient(to top, var(--error), var(--warning))',
                  }}
                >
                  <div className="bar-value">{count}</div>
                  <div className="bar-label">{type.replace(/_/g, ' ')}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recent Traces */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Traces</h3>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/traces')}>
            View All →
          </button>
        </div>

        {recentTraces.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No traces yet</h3>
            <p>Run the demo to process 50 sample documents and populate the dashboard.</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Trace ID</th>
                  <th>Status</th>
                  <th>Failure Type</th>
                  <th>Confidence</th>
                  <th>Latency</th>
                  <th>Created</th>
                  <th>Flagged</th>
                </tr>
              </thead>
              <tbody>
                {recentTraces.map(trace => (
                  <tr
                    key={trace.trace_id}
                    onClick={() => navigate(`/traces/${trace.trace_id}`)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>
                      <code style={{ fontSize: '12px', color: 'var(--accent)' }}>
                        {trace.trace_id?.slice(0, 8)}...
                      </code>
                    </td>
                    <td><StatusBadge status={trace.status} /></td>
                    <td><FailureTypeBadge type={trace.failure_type} /></td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px' }}>
                        {(trace.avg_confidence || 0).toFixed(1)}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px' }}>
                        {(trace.total_latency_ms || 0).toFixed(0)}ms
                      </span>
                    </td>
                    <td style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                      {new Date(trace.created_at).toLocaleString()}
                    </td>
                    <td>{trace.flagged ? '🚩' : ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
