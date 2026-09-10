import { Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, FolderSearch, AlertTriangle, Users, Network } from 'lucide-react';
import Dashboard from './components/Dashboard';
import ProjectExplorer from './components/ProjectExplorer';
import ProjectInvestigation from './components/ProjectInvestigation';
import VendorIntelligence from './components/VendorIntelligence';
import NetworkVisualization from './components/NetworkVisualization';

function App() {
  return (
    <div className="app-container">
      <div className="sidebar">
        <h1>NEXORAS</h1>
        <nav>
          <NavLink to="/" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <LayoutDashboard size={20} /> Dashboard
          </NavLink>
          <NavLink to="/projects" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <FolderSearch size={20} /> Projects
          </NavLink>
          <NavLink to="/anomalies" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <AlertTriangle size={20} /> Anomalies
          </NavLink>
          <NavLink to="/vendors" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <Users size={20} /> Vendors
          </NavLink>
          <NavLink to="/network" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <Network size={20} /> Network Graph
          </NavLink>
        </nav>
      </div>
      <div className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<ProjectExplorer />} />
          <Route path="/projects/:id" element={<ProjectInvestigation />} />
          <Route path="/anomalies" element={<ProjectExplorer filterAnomalies={true} />} />
          <Route path="/vendors" element={<VendorIntelligence />} />
          <Route path="/network" element={<NetworkVisualization />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
