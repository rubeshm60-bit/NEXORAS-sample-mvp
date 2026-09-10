import { useState, useEffect } from 'react';
import axios from 'axios';
import CytoscapeComponent from 'react-cytoscapejs';

export default function NetworkVisualization() {
  const [elements, setElements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8000/network')
      .then(res => {
        const { nodes, edges } = res.data;
        setElements([...nodes, ...edges]);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading network graph...</div>;

  const style = [
    {
      selector: 'node[type="mp"]',
      style: {
        'background-color': '#ef4444',
        'label': 'data(label)',
        'color': '#fff',
        'text-valign': 'center',
        'text-halign': 'center',
        'width': 60,
        'height': 60
      }
    },
    {
      selector: 'node[type="vendor"]',
      style: {
        'background-color': '#3b82f6',
        'label': 'data(label)',
        'color': '#fff',
        'text-valign': 'center',
        'text-halign': 'center',
        'width': 40,
        'height': 40
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#cbd5e1',
        'curve-style': 'bezier'
      }
    }
  ];

  return (
    <div className="card" style={{ height: '80vh' }}>
      <h2>Cartel & Monopoly Network Discovery</h2>
      <p style={{color: 'var(--text-light)', marginBottom: '20px'}}>
        Visualizing relationships between MPs (Red) and Contractors (Blue).
      </p>
      
      <div style={{ height: 'calc(100% - 80px)', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#f8fafc' }}>
        <CytoscapeComponent 
          elements={elements} 
          style={{ width: '100%', height: '100%' }} 
          stylesheet={style}
          layout={{ name: 'cose' }} // Compound Spring Embedder for nice network layout
        />
      </div>
    </div>
  );
}
