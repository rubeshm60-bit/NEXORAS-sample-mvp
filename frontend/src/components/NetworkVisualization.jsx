import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import CytoscapeComponent from 'react-cytoscapejs';
import { Network, Search, Filter, IndianRupee, Users } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function NetworkVisualization() {
  const [elements, setElements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const cyRef = useRef(null);

  useEffect(() => {
    axios.get(`${API_URL}/network`)
      .then(res => {
        const { nodes, edges } = res.data;
        
        // Add dynamic scaling classes or data attributes
        const formattedNodes = nodes.map(n => {
          if (n.data.type === 'vendor') {
            // scale vendor size between 30 and 80 based on payout
            const size = Math.min(80, Math.max(30, (n.data.payout || 0) / 1000000));
            return { ...n, data: { ...n.data, size } };
          }
          return { ...n, data: { ...n.data, size: 60 } };
        });

        const formattedEdges = edges.map(e => {
            // scale edge width based on weight (transaction amount)
            const width = Math.min(8, Math.max(1, (e.data.weight || 0) / 2000000));
            return { ...e, data: { ...e.data, width } };
        });

        setElements([...formattedNodes, ...formattedEdges]);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleNodeClick = (evt) => {
    const node = evt.target;
    setSelectedNode(node.data());
    
    // Highlight connected edges and nodes
    if (cyRef.current) {
        const cy = cyRef.current;
        cy.elements().removeClass('highlighted faded');
        
        const neighborhood = node.neighborhood();
        cy.elements().difference(neighborhood).not(node).addClass('faded');
        neighborhood.addClass('highlighted');
        node.addClass('highlighted');
    }
  };

  const resetHighlight = () => {
    if (cyRef.current) {
        cyRef.current.elements().removeClass('highlighted faded');
    }
    setSelectedNode(null);
  };

  if (loading) return <div>Loading complex network graph... This may take a few seconds.</div>;

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
    },
    {
      selector: '.faded',
      style: {
        'opacity': 0.1
      }
    },
    {
      selector: 'node.highlighted',
      style: {
        'border-color': '#fbbf24',
        'border-width': 4
      }
    },
    {
      selector: 'edge.highlighted',
      style: {
        'line-color': '#fbbf24',
        'opacity': 1,
        'z-index': 10
      }
    }
  ];

  return (
    <div style={{ display: 'flex', gap: '20px', height: '85vh' }}>
      
      {/* GRAPH CONTAINER */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px', margin: 0 }}>
                <Network size={24} /> Vendor-MP Syndicate Intelligence
            </h2>
            <button className="btn" onClick={resetHighlight} style={{ padding: '5px 10px', fontSize: '12px' }}>
                Reset View
            </button>
        </div>
        <p style={{color: 'var(--text-light)', fontSize: '14px', marginBottom: '15px'}}>
          Hexagons = MPs (Red) | Circles = Vendors (Blue). Larger vendors have received more funds. 
          Click any node to investigate relationships.
        </p>
        
        <div style={{ flex: 1, border: '1px solid #e2e8f0', borderRadius: '8px', background: '#f8fafc', overflow: 'hidden' }}>
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
                cy.on('tap', 'node', handleNodeClick);
                cy.on('tap', (e) => {
                    if (e.target === cy) resetHighlight();
                });
            }}
          />
        </div>
      </div>

      {/* INTELLIGENCE PANEL */}
      <div className="card" style={{ width: '350px', overflowY: 'auto' }}>
        <h3 style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '10px', marginBottom: '20px' }}>
            Node Intelligence
        </h3>
        
        {!selectedNode ? (
            <div style={{ textAlign: 'center', color: '#94a3b8', marginTop: '50px' }}>
                <Search size={48} style={{ opacity: 0.5, marginBottom: '15px' }} />
                <p>Select a node in the graph to view intelligence details.</p>
            </div>
        ) : (
            <div>
                <div style={{ 
                    display: 'inline-block',
                    padding: '4px 10px', 
                    background: selectedNode.type === 'mp' ? '#fee2e2' : '#dbeafe',
                    color: selectedNode.type === 'mp' ? '#991b1b' : '#1e40af',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    marginBottom: '15px'
                }}>
                    {selectedNode.type === 'mp' ? 'Member of Parliament' : 'Contractor / Vendor'}
                </div>
                
                <h2 style={{ fontSize: '20px', marginBottom: '20px', wordBreak: 'break-word' }}>
                    {selectedNode.label}
                </h2>

                {selectedNode.type === 'vendor' && (
                    <>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
                            <div style={{ background: '#f1f5f9', padding: '10px', borderRadius: '8px', flex: 1 }}>
                                <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                    <IndianRupee size={14} /> Total Payout
                                </div>
                                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                    ₹{(selectedNode.payout || 0).toLocaleString()}
                                </div>
                            </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                            <div style={{ background: '#f1f5f9', padding: '10px', borderRadius: '8px', flex: 1 }}>
                                <div style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                    <Users size={14} /> Connected MPs
                                </div>
                                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                    {selectedNode.mp_count || 1}
                                </div>
                            </div>
                        </div>

                        {selectedNode.mp_count > 1 && (
                            <div style={{ padding: '15px', background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '8px', color: '#991b1b', fontSize: '14px' }}>
                                <strong>⚠️ Syndicate Risk:</strong> This vendor serves multiple MPs, indicating a potential monopoly or cartel arrangement in the region.
                            </div>
                        )}
                    </>
                )}
                
                {selectedNode.type === 'mp' && (
                    <div style={{ fontSize: '14px', color: '#475569' }}>
                        <p>This node represents a Member of Parliament.</p>
                        <p>In the graph, you can see all contractors (blue circles) who have received funds authorized by this MP.</p>
                        <p>Heavy lines indicate larger transaction volumes.</p>
                    </div>
                )}
            </div>
        )}
      </div>
    </div>
  );
}
