import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import TraceList from './pages/TraceList';
import TraceDetail from './pages/TraceDetail';
import Analytics from './pages/Analytics';
import EvalDataset from './pages/EvalDataset';
import RunPipeline from './pages/RunPipeline';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/traces" element={<TraceList />} />
            <Route path="/traces/:traceId" element={<TraceDetail />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/eval" element={<EvalDataset />} />
            <Route path="/run" element={<RunPipeline />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
