import { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // We assume backend is running on http://localhost:8000
    axios.get('http://localhost:8000/dashboard/summary')
      .then(res => {
        setStats(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading dashboard...</div>;
  if (!stats) return <div>Error loading data. Is the backend running?</div>;

  return (
    <div>
      <h2>NEXORAS Executive Dashboard</h2>
      
      <div className="grid-3">
        <div className="stat-box">
          <div>Total Projects Monitored</div>
          <div className="stat-value">{stats.total_projects.toLocaleString()}</div>
        </div>
        <div className="stat-box">
          <div>Total Value (Lakh)</div>
          <div className="stat-value">₹{stats.total_value.toLocaleString()}</div>
        </div>
        <div className="stat-box" style={{border: '1px solid var(--critical)'}}>
          <div style={{color: 'var(--critical)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px'}}>
            <AlertTriangle size={18} /> High Risk Anomalies
          </div>
          <div className="stat-value" style={{color: 'var(--critical)'}}>
            {stats.high_risk_projects.toLocaleString()}
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Risk Distribution</h3>
        <div style={{display: 'flex', gap: '20px', marginTop: '10px'}}>
          <div style={{padding: '10px', background: '#fef2f2', border: '1px solid var(--critical)', borderRadius: '4px', flex: 1}}>
            <strong>Critical / High:</strong> {stats.high_risk_projects}
          </div>
          <div style={{padding: '10px', background: '#fefce8', border: '1px solid var(--medium)', borderRadius: '4px', flex: 1}}>
            <strong>Medium Risk:</strong> {stats.medium_risk_projects}
          </div>
          <div style={{padding: '10px', background: '#f0fdf4', border: '1px solid var(--low)', borderRadius: '4px', flex: 1}}>
            <strong>Low Risk:</strong> {stats.low_risk_projects}
          </div>
        </div>
      </div>
    </div>
  );
}
