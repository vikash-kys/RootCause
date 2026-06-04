import { useState, useEffect } from 'react';
import { getEvalDataset, runRegression, getRegressionHistory } from '../api';
import { LoadingSpinner, EmptyState, FailureTypeBadge } from '../components/shared';

export default function EvalDataset() {
  const [dataset, setDataset] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [regressionRunning, setRegressionRunning] = useState(false);
  const [regressionResult, setRegressionResult] = useState(null);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [evalData, historyData] = await Promise.all([
        getEvalDataset(),
        getRegressionHistory(),
      ]);
      setDataset(evalData);
      setHistory(historyData.runs || []);
    } catch (err) {
      console.error('Failed to fetch eval data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunRegression = async () => {
    setRegressionRunning(true);
    setRegressionResult(null);
    try {
      const result = await runRegression();
      setRegressionResult(result);
      await fetchData();
    } catch (err) {
      console.error('Regression failed:', err);
    } finally {
      setRegressionRunning(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading eval dataset..." />;

  const cases = dataset?.cases || [];
  const stats = dataset?.stats || {};

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2>Evaluation Dataset</h2>
            <p>Growing test suite built from flagged failures and human feedback</p>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleRunRegression}
            disabled={regressionRunning || cases.length === 0}
          >
            {regressionRunning ? '⟳ Running regression...' : '▷ Run Regression Tests'}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">✓</div>
          <div className="stat-value">{stats.total || 0}</div>
          <div className="stat-label">Total Cases</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ color: 'var(--error)' }}>✕</div>
          <div className="stat-value" style={{ color: 'var(--error)' }}>{stats.unresolved || 0}</div>
          <div className="stat-label">Unresolved</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ color: 'var(--success)' }}>✓</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.resolved || 0}</div>
          <div className="stat-label">Resolved</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">↻</div>
          <div className="stat-value">{history.length}</div>
          <div className="stat-label">Regression Runs</div>
        </div>
      </div>

      {/* Regression Result */}
      {regressionResult && (
        <div className="card" style={{ marginBottom: '24px', borderColor: 'var(--info-border)' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Regression Results</h3>
          <div style={{ display: 'flex', gap: '24px' }}>
            <div>
              <span style={{ fontSize: '24px', fontWeight: 700, color: 'var(--error)' }}>{regressionResult.still_failing}</span>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)', marginLeft: '6px' }}>still failing</span>
            </div>
            <div>
              <span style={{ fontSize: '24px', fontWeight: 700, color: 'var(--success)' }}>{regressionResult.resolved}</span>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)', marginLeft: '6px' }}>resolved</span>
            </div>
            <div>
              <span style={{ fontSize: '24px', fontWeight: 700 }}>{regressionResult.total_cases}</span>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)', marginLeft: '6px' }}>total cases</span>
            </div>
          </div>
        </div>
      )}

      {/* Eval Cases Table */}
      {cases.length === 0 ? (
        <EmptyState
          icon="📋"
          title="No eval cases yet"
          message="Flag traces with bad output and confirm the diagnosis to build your evaluation dataset."
        />
      ) : (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Eval Cases ({cases.length})</h3>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Eval ID</th>
                  <th>Failing Step</th>
                  <th>Failure Type</th>
                  <th>Status</th>
                  <th>Input Preview</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {cases.map(c => (
                  <tr key={c.eval_id}>
                    <td>
                      <code style={{ fontSize: '12px', color: 'var(--accent)' }}>
                        {c.eval_id?.slice(0, 8)}...
                      </code>
                    </td>
                    <td>
                      <span className="badge badge-info" style={{ fontSize: '11px' }}>
                        {c.failing_step}
                      </span>
                    </td>
                    <td><FailureTypeBadge type={c.failure_type} /></td>
                    <td>
                      {c.resolved ? (
                        <span className="badge badge-success">Resolved</span>
                      ) : (
                        <span className="badge badge-error">Open</span>
                      )}
                    </td>
                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '13px', color: 'var(--text-muted)' }}>
                      {c.original_input?.slice(0, 100)}...
                    </td>
                    <td style={{ fontSize: '12px', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      {new Date(c.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Regression History */}
      {history.length > 0 && (
        <div className="card" style={{ marginTop: '24px' }}>
          <div className="card-header">
            <h3 className="card-title">Regression Run History</h3>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Total Cases</th>
                  <th>Still Failing</th>
                  <th>Resolved</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {history.map(run => (
                  <tr key={run.run_id}>
                    <td><code style={{ fontSize: '12px' }}>{run.run_id?.slice(0, 8)}...</code></td>
                    <td>{run.total_cases}</td>
                    <td style={{ color: 'var(--error)' }}>{run.still_failing}</td>
                    <td style={{ color: 'var(--success)' }}>{run.resolved}</td>
                    <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      {new Date(run.run_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
