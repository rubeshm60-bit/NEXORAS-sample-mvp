import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

export default function ProjectInvestigation() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`http://localhost:8000/projects/${id}`)
      .then(res => {
        setProject(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div>Loading investigation...</div>;
  if (!project) return <div>Project not found.</div>;

  const rs = project.risk_score;

  return (
    <div>
      <Link to="/projects" style={{textDecoration: 'none', color: 'var(--primary)', marginBottom: '20px', display: 'block'}}>
        &larr; Back to Projects
      </Link>
      
      <div className="card">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
          <div>
            <h2>{project.work_name}</h2>
            <div style={{color: 'var(--text-light)', marginBottom: '20px'}}>ID: {project.id} | MP: {project.mp_id}</div>
          </div>
          {rs && (
            <div style={{textAlign: 'right'}}>
              <div style={{fontSize: '14px', color: 'var(--text-light)'}}>Unified Risk Score</div>
              <div className={`stat-value tier-${rs.risk_tier}`}>{rs.unified_score.toFixed(1)} / 100</div>
              <div className={`tier-${rs.risk_tier}`}>{rs.risk_tier.replace('_', ' ')}</div>
            </div>
          )}
        </div>

        <div className="grid-3" style={{marginTop: '20px'}}>
          <div style={{background: '#f8fafc', padding: '15px', borderRadius: '4px'}}>
            <strong>Financial Details</strong>
            <div style={{marginTop: '10px'}}>Sanctioned: ₹{project.sanctioned_amount}</div>
            <div>Final Amount: ₹{project.final_amount}</div>
            <div>Status: {project.status}</div>
          </div>
          
          {rs && (
            <div style={{background: '#f8fafc', padding: '15px', borderRadius: '4px', gridColumn: 'span 2'}}>
              <strong>Risk Score Breakdown</strong>
              <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '10px'}}>
                <div>Tabular (25%): <strong>{rs.tabular_pts.toFixed(1)} pts</strong></div>
                <div>Network (25%): <strong>{rs.network_pts.toFixed(1)} pts</strong></div>
                <div>Graph (20%): <strong>{rs.graph_pts.toFixed(1)} pts</strong></div>
                <div>Finance (15%): <strong>{rs.financial_pts.toFixed(1)} pts</strong></div>
                <div>NLP (15%): <strong>{rs.nlp_pts.toFixed(1)} pts</strong></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {rs && rs.why_flagged_report && (
        <div className="card">
          <h3 style={{color: 'var(--critical)', marginTop: 0}}>Audit Evidence: Why Flagged?</h3>
          <p style={{color: 'var(--text-light)'}}>The following patterns contributed significantly to the risk score:</p>
          <div className="why-flagged-block">
            <pre>{rs.why_flagged_report}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
