import { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, FileText } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [contractSplitting, setContractSplitting] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch summary and contract splitting alerts concurrently
    Promise.all([
      axios.get(`${API_URL}/dashboard/summary`),
      axios.get(`${API_URL}/nlp/contract-splitting`)
    ]).then(([summaryRes, nlpRes]) => {
      setStats(summaryRes.data);
      setContractSplitting(nlpRes.data.items || []);
      setLoading(false);
    }).catch(err => {
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
      
      <div className="card" style={{marginTop: '20px'}}>
        <h3 style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
          <FileText size={20} /> NLP Contract Splitting Alerts
        </h3>
        <p style={{color: 'var(--text-light)', marginBottom: '15px'}}>
          Identifies potential contract splitting (identical project descriptions repeated multiple times just below the ₹50L threshold).
        </p>
        
        {contractSplitting.length === 0 ? (
          <div style={{padding: '20px', textAlign: 'center', background: '#f8fafc', borderRadius: '4px'}}>
            No contract splitting patterns detected.
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>MP Name</th>
                <th>Constituency</th>
                <th>Repeated Project Description</th>
                <th>Repetitions</th>
                <th>Risk Score</th>
              </tr>
            </thead>
            <tbody>
              {contractSplitting.map((alert, idx) => (
                <tr key={idx}>
                  <td><strong>{alert.mp_name}</strong></td>
                  <td>{alert.constituency}</td>
                  <td><span className="badge">{alert.description_text}</span></td>
                  <td>{alert.repeat_count}x</td>
                  <td style={{color: alert.nlp_risk_score > 60 ? 'var(--critical)' : 'inherit'}}>
                    {alert.nlp_risk_score.toFixed(1)} / 100
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
