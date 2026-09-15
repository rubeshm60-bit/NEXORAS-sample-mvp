import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';


let vendorCache = null;

export default function VendorIntelligence() {
  const [vendors, setVendors] = useState(vendorCache || []);
  const [loading, setLoading] = useState(!vendorCache);

  useEffect(() => {
    // If we already downloaded the massive vendor list, load instantly!
    if (vendorCache) return;

    axios.get(`${API_URL}/vendors?limit=5000`)
      .then(res => {
        vendorCache = res.data.items; // Save to memory
        setVendors(res.data.items);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading vendors...</div>;

  return (
    <div className="card">
      <h2>Vendor Intelligence</h2>
      <p>Analyze contractor monopolies and multi-MP syndicates.</p>
      
      <table>
        <thead>
          <tr>
            <th>Vendor Name</th>
            <th>Total Payout</th>
            <th>Txn Count</th>
            <th>Unique MPs</th>
            <th>Risk Profile</th>
          </tr>
        </thead>
        <tbody>
          {vendors.map(v => (
            <tr key={v.id}>
              <td>{v.name}</td>
              <td>₹{v.total_payout.toLocaleString('en-IN')}</td>
              <td>{v.transaction_count}</td>
              <td>{v.mp_count}</td>
              <td>
                {v.risk_profile?.flags ? (
                  <span style={{color: 'var(--critical)', fontWeight: 'bold'}}>{v.risk_profile.flags}</span>
                ) : (
                  <span style={{color: 'var(--text-light)'}}>Normal</span>
                )}
              </td>
            </tr>
          ))}
          {vendors.length === 0 && (
            <tr><td colSpan="5" style={{textAlign: 'center'}}>No vendors found.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

