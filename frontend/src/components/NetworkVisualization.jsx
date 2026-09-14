import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import CytoscapeComponent from 'react-cytoscapejs';
import { Network, Search, Users, IndianRupee } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function NetworkVisualization() {
  const [vendors, setVendors] = useState([]);
  const [selectedVendorId, setSelectedVendorId] = useState(null);
  const [elements, setElements] = useState([]);
  const [loadingGraph, setLoadingGraph] = useState(false);
  const [vendorProjects, setVendorProjects] = useState([]);
  const cyRef = useRef(null);

  useEffect(() => {
    // Load vendors list
    axios.get(`${API_URL}/vendors?limit=100`)
      .then(res => {
        setVendors(res.data.items);
      })
      .catch(console.error);
  }, []);

  const handleVendorSelect = (vendor) => {
    setSelectedVendorId(vendor.id);
    setLoadingGraph(true);
    
    // Fetch network graph for this specific vendor
    axios.get(`${API_URL}/network?vendor_id=${vendor.id}`)
      .then(res => {
        const { nodes, edges } = res.data;
        
        const formattedNodes = nodes.map(n => {
          if (n.data.type === 'vendor') {
            const size = Math.min(80, Math.max(30, (n.data.payout || 0) / 1000000));
            return { ...n, data: { ...n.data, size } };
          }
          return { ...n, data: { ...n.data, size: 60 } };
        });

        const formattedEdges = edges.map(e => {
            const width = Math.min(8, Math.max(1, (e.data.weight || 0) / 2000000));
            return { ...e, data: { ...e.data, width } };
        });

        setElements([...formattedNodes, ...formattedEdges]);
        setLoadingGraph(false);
      })
      .catch(err => {
        console.error(err);
        setLoadingGraph(false);
      });

    // Fetch projects for this vendor
    axios.get(`${API_URL}/vendors/${vendor.id}/projects`)
      .then(res => {
        setVendorProjects(res.data);
      })
      .catch(console.error);
  };

  const style = [
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'font-size': '10px',
        'color': '#1e293b',
        'text-valign': 'bottom',
        'text-margin-y': 5,
        'transition-property': 'background-color, line-color, target-arrow-color, opacity',
        'transition-duration': '0.3s'
      }
    },
    {
      selector: 'node[type="mp"]',
      style: {
        'background-color': '#dc2626', // Red for MPs
        'width': 'data(size)',
        'height': 'data(size)',
        'shape': 'hexagon',
        'border-width': 2,
        'border-color': '#991b1b'
      }
    },
    {
      selector: 'node[type="vendor"]',
      style: {
        'background-color': '#2563eb', // Blue for Vendors
        'width': 'data(size)',
        'height': 'data(size)',
        'shape': 'ellipse',
        'border-width': 2,
        'border-color': '#1e40af'
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 'data(width)',
        'line-color': '#cbd5e1',
        'curve-style': 'bezier',
        'opacity': 0.6
      }
    }
  ];

  return (
    <div style={{ display: 'flex', gap: '20px', height: '85vh' }}>
      
      {/* VENDOR LIST (LEFT SIDEBAR) */}
      <div className="card" style={{ width: '300px', display: 'flex', flexDirection: 'column' }}>
        <h3 style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '10px', margin: '0 0 10px 0' }}>
            Vendors List
        </h3>
        <p style={{fontSize: '12px', color: 'var(--text-light)', marginBottom: '15px'}}>Click a vendor to view their network graph.</p>
        <div style={{ flex: 1, overflowY: 'auto' }}>
            {vendors.map(v => (
                <div 
                    key={v.id} 
                    onClick={() => handleVendorSelect(v)}
                    style={{ 
                        padding: '10px', 
                        borderBottom: '1px solid #e2e8f0',
                        cursor: 'pointer',
                        background: selectedVendorId === v.id ? '#eff6ff' : 'white',
                        borderLeft: selectedVendorId === v.id ? '4px solid #3b82f6' : '4px solid transparent'
                    }}
                >
                    <div style={{fontWeight: 'bold', fontSize: '14px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                        {v.name}
                    </div>
                    <div style={{fontSize: '12px', color: 'var(--text-light)'}}>
                        ₹{v.total_payout.toLocaleString('en-IN')} | {v.mp_count} MPs
                    </div>
                </div>
            ))}
        </div>
      </div>

      {/* GRAPH CONTAINER */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px', margin: 0 }}>
                <Network size={24} /> Vendor Network Graph
            </h2>
        </div>
        
        <div style={{ flex: 1, border: '1px solid #e2e8f0', borderRadius: '8px', background: '#f8fafc', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {!selectedVendorId ? (
              <div style={{ color: '#94a3b8', textAlign: 'center' }}>
                  <Network size={48} style={{ opacity: 0.5, marginBottom: '15px' }} />
                  <p>Select a vendor from the list to display their graph.</p>
              </div>
          ) : loadingGraph ? (
              <div>Loading graph data...</div>
          ) : (
              <CytoscapeComponent 
                elements={elements} 
                style={{ width: '100%', height: '100%' }} 
                stylesheet={style}
                layout={{ 
                    name: 'cose',
                    idealEdgeLength: 100,
                    nodeOverlap: 20,
                    refresh: 20,
                    fit: true,
                    padding: 30,
                    randomize: false,
                    componentSpacing: 100,
                    nodeRepulsion: 400000,
                    edgeElasticity: 100,
                    nestingFactor: 5
                }} 
                cy={(cy) => {
                    cyRef.current = cy;
                }}
              />
          )}
        </div>
      </div>

      {/* PROJECTS PANEL (RIGHT SIDEBAR) */}
      <div className="card" style={{ width: '350px', display: 'flex', flexDirection: 'column' }}>
        <h3 style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '10px', margin: '0 0 10px 0' }}>
            Vendor Projects
        </h3>
        
        {!selectedVendorId ? (
            <div style={{ textAlign: 'center', color: '#94a3b8', marginTop: '50px' }}>
                <Search size={48} style={{ opacity: 0.5, marginBottom: '15px' }} />
                <p>Select a vendor to view their projects.</p>
            </div>
        ) : (
            <div style={{ flex: 1, overflowY: 'auto' }}>
                {vendorProjects.length === 0 ? (
                    <div style={{ color: 'var(--text-light)', fontSize: '14px', textAlign: 'center', marginTop: '20px' }}>
                        No projects found for this vendor.
                    </div>
                ) : (
                    vendorProjects.map(p => (
                        <div key={p.id} style={{ padding: '12px', borderBottom: '1px solid #e2e8f0', fontSize: '14px' }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{p.work_name}</div>
                            <div style={{ color: 'var(--text-light)' }}>ID: {p.id}</div>
                            <div style={{ color: 'var(--text-light)' }}>Final Amount: ₹{Number(p.final_amount).toLocaleString('en-IN')}</div>
                            <div style={{ color: 'var(--text-light)' }}>MP: {p.mp_name || 'Unknown'}</div>
                        </div>
                    ))
                )}
            </div>
        )}
      </div>
    </div>
  );
}
