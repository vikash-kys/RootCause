import { useState, useEffect } from 'react';
import { getAnalytics, getTrends, getTaxonomy } from '../api';
import { LoadingSpinner } from '../components/shared';

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [trends, setTrends] = useState([]);
  const [taxonomy, setTaxonomy] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [analyticsData, trendsData, taxonomyData] = await Promise.all([
        getAnalytics(),
        getTrends(30),
        getTaxonomy(),
      ]);
      setAnalytics(analyticsData);
      setTrends(trendsData.trends || []);
      setTaxonomy(taxonomyData.taxonomy || {});
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading analytics..." />;

  const stats = analytics || {};
  const failureTypes = stats.failure_by_type || {};
  const maxFailure = Math.max(...Object.values(failureTypes), 1);

  const colors = {
    extraction_hallucination: '#f87171',
    misclassification: '#fbbf24',
    propagation_error: '#60a5fa',
    prompt_failure: '#a78bfa',
    context_loss: '#fb923c',
  };

  return (
    <div>
      <div className="page-header">
        <h2>Failure Analytics</h2>
        <p>Insights into pipeline failures — what breaks, where, and how often</p>
      </div>

      {/* Summary stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">◎</div>
          <div className="stat-value">{((stats.failure_rate || 0) * 100).toFixed(1)}%</div>
          <div className="stat-label">Failure Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⊡</div>
          <div className="stat-value">{stats.total_traces || 0}</div>
          <div className="stat-label">Total Traces</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ color: 'var(--success)' }}>⏱</div>
          <div className="stat-value">{(stats.avg_latency_ms || 0).toFixed(0)}<span style={{ fontSize: '14px', fontWeight: 400 }}>ms</span></div>
          <div className="stat-label">Avg Latency</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">★</div>
          <div className="stat-value">{(stats.avg_confidence || 0).toFixed(1)}</div>
          <div className="stat-label">Avg Confidence</div>
        </div>
      </div>

      {/* Failure Types Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Failure Types Distribution</h3>
          </div>
          {Object.keys(failureTypes).length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>No failures recorded yet</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {Object.entries(failureTypes).map(([type, count]) => (
                <div key={type}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 500 }}>
                      {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-muted)' }}>
                      {count}
                    </span>
                  </div>
                  <div style={{ height: '8px', background: 'var(--bg-primary)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${(count / maxFailure) * 100}%`,
                      background: colors[type] || 'var(--accent)',
                      borderRadius: '4px',
                      transition: 'width 0.5s ease',
                    }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Status Distribution</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '12px 0' }}>
            {[
              { label: 'Success', count: stats.success_count || 0, color: 'var(--success)' },
              { label: 'Degraded', count: stats.degraded_count || 0, color: 'var(--warning)' },
              { label: 'Failure', count: stats.failure_count || 0, color: 'var(--error)' },
            ].map(item => {
              const total = stats.total_traces || 1;
              const pct = ((item.count / total) * 100).toFixed(1);
              return (
                <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ width: '80px', textAlign: 'right' }}>
                    <span style={{ fontSize: '20px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: item.color }}>
                      {item.count}
                    </span>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 500 }}>{item.label}</span>
                      <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{pct}%</span>
                    </div>
                    <div style={{ height: '6px', background: 'var(--bg-primary)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{
                        height: '100%',
                        width: `${pct}%`,
                        background: item.color,
                        borderRadius: '3px',
                        transition: 'width 0.5s ease',
                      }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Trend Chart */}
      {trends.length > 0 && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-header">
            <h3 className="card-title">Failure Rate Over Time</h3>
          </div>
          <div className="bar-chart" style={{ height: '200px', paddingBottom: '40px' }}>
            {trends.map((point, i) => {
              const maxTotal = Math.max(...trends.map(t => t.total), 1);
              const totalH = (point.total / maxTotal) * 100;
              const failH = (point.failures / maxTotal) * 100;

              return (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative', height: '100%', justifyContent: 'flex-end' }}>
                  <div style={{ width: '100%', display: 'flex', gap: '2px', alignItems: 'flex-end', justifyContent: 'center', height: '100%' }}>
                    <div style={{ width: '40%', height: `${totalH}%`, background: 'var(--info)', borderRadius: '3px 3px 0 0', opacity: 0.3, minHeight: '2px' }} />
                    <div style={{ width: '40%', height: `${failH}%`, background: 'var(--error)', borderRadius: '3px 3px 0 0', minHeight: point.failures > 0 ? '2px' : '0' }} />
                  </div>
                  <div style={{ fontSize: '9px', color: 'var(--text-muted)', marginTop: '8px', transform: 'rotate(-45deg)', whiteSpace: 'nowrap' }}>
                    {point.date?.slice(5)}
                  </div>
                </div>
              );
            })}
          </div>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '8px' }}>
            <span style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '2px', background: 'var(--info)', opacity: 0.3, display: 'inline-block' }} />
              Total
            </span>
            <span style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '2px', background: 'var(--error)', display: 'inline-block' }} />
              Failures
            </span>
          </div>
        </div>
      )}

      {/* Failure Taxonomy */}
      {Object.keys(taxonomy).length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Failure Type Taxonomy</h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
            {Object.entries(taxonomy).map(([type, info]) => (
              <div
                key={type}
                style={{
                  padding: '16px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-primary)',
                  background: 'var(--bg-glass)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 600 }}>{info.name}</h4>
                  <span className={`badge ${info.severity === 'high' ? 'badge-error' : 'badge-warning'}`} style={{ fontSize: '10px' }}>
                    {info.severity}
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  {info.description}
                </p>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Typical step: {info.typical_step}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
