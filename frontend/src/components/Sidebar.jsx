import { NavLink, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/', icon: '◈', label: 'Dashboard' },
  { path: '/traces', icon: '⊡', label: 'Traces' },
  { path: '/run', icon: '▷', label: 'Run Pipeline' },
  { path: '/analytics', icon: '◎', label: 'Analytics' },
  { path: '/eval', icon: '✓', label: 'Eval Dataset' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon">FF</div>
          <div>
            <h1>Failure Forensics</h1>
            <div className="logo-subtitle">AI Pipeline Observability</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Navigation</div>
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
            end={item.path === '/'}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}

        <div className="nav-section-label" style={{ marginTop: 'auto' }}>System</div>
        <div className="nav-link" style={{ opacity: 0.5, cursor: 'default' }}>
          <span className="nav-icon">●</span>
          <span style={{ fontSize: '12px' }}>Mock LLM Active</span>
        </div>
      </nav>
    </aside>
  );
}
