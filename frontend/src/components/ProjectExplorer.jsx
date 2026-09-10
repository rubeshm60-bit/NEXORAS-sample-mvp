import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

export default function ProjectExplorer({ filterAnomalies = false }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = filterAnomalies 
      ? 'http://localhost:8000/anomalies?limit=50' 
      : 'http://localhost:8000/projects?limit=50';
      
    axios.get(url)
      .then(res => {
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
          {projects.map(p => (
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
    </div>
  );
}
