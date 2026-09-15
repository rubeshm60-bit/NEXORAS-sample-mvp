import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';


let projectCache = { projects: null, anomalies: null };

export default function ProjectExplorer({ filterAnomalies = false }) {
  const cacheKey = filterAnomalies ? 'anomalies' : 'projects';
  const [projects, setProjects] = useState(projectCache[cacheKey] || []);
  const [loading, setLoading] = useState(!projectCache[cacheKey]);

  useEffect(() => {
    // 1. If we already downloaded the data, update the screen instantly!
    if (projectCache[cacheKey]) {
      setProjects(projectCache[cacheKey]);
      setLoading(false);
      return;
    }

    // 2. Otherwise, show loading and fetch from backend
    setLoading(true);
    const url = filterAnomalies 
      ? `${API_URL}/anomalies?limit=5000` 
      : `${API_URL}/projects?limit=5000`;
      
    axios.get(url)
      .then(res => {
        projectCache[cacheKey] = res.data.items; // Save to memory
        setProjects(res.data.items);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [filterAnomalies]);

  if (loading) return <div>Loading projects...</div>;

  return (
    <div className="card">
      <h2>{filterAnomalies ? 'High Risk Anomalies' : 'Project Explorer'}</h2>
      
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Work Name</th>
            <th>Sanctioned Amount</th>
            <th>Risk Tier</th>
            <th>Score</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {projects.slice(0, 100).map(p => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td style={{maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{p.work_name}</td>
              <td>₹{p.sanctioned_amount}</td>
              <td className={`tier-${p.risk_score?.risk_tier || 'LOW_RISK'}`}>
                {p.risk_score?.risk_tier.replace('_', ' ') || 'LOW RISK'}
              </td>
              <td>
                {p.risk_score?.unified_score ? p.risk_score.unified_score.toFixed(1) : 'N/A'}
              </td>
              <td>
                <Link to={`/projects/${p.id}`} className="btn">Investigate</Link>
              </td>
            </tr>
          ))}
          {projects.length === 0 && (
            <tr><td colSpan="6" style={{textAlign: 'center'}}>No projects found.</td></tr>
          )}
        </tbody>
      </table>
      {projects.length > 100 && (
        <div style={{textAlign: 'center', marginTop: '15px', padding: '10px', color: '#64748b'}}>
          Showing Top 100 of {projects.length} loaded records for maximum performance.
        </div>
      )}
    </div>
  );
}

