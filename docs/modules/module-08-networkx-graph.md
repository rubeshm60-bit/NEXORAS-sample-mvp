# MODULE 08 — NETWORKX GRAPH ENGINE

## Purpose
Construct large-scale heterogeneous and bipartite topological graph networks mapping public fund flows across Members of Parliament (MPs), Commercial Contractors (Vendors), and Implementing District Authorities (IDAs). Execute graph analytics including PageRank, Betweenness Centrality, Louvain Community Detection, and Bipartite Clique Analysis to expose structural collusion, procurement hubs, and regional contracting consortiums.

## Why NEXORAS Needs It
Tabular anomaly detection (Isolation Forest and Autoencoder) operates on row-wise feature vectors in isolation; it cannot see the **topological web of connections** through which public funds travel.
In the MPLADS expenditure records:
- An individual MP might appear statistically benign in isolation, yet share a closed network of contractors with multiple neighboring constituencies.
- Certain high-influence contractors act as national or regional **hubs**, channeling tens of crores across diverse administrative districts.
- Certain entities act as **structural bridges** (high betweenness centrality) connecting otherwise disjoint clusters of constituencies.
- Module 8 turns relational transaction tables into a mathematical graph of **29,745 nodes and 64,375 edges**, revealing macroscopic corruption topology invisible to standard tabular ML.

## Graph Architecture & Topology

### 1. Heterogeneous Tripartite Graph ($G_{\text{Full}}$)
- **Node Types**:
  - `MP`: 774 nodes (Parliamentarians)
  - `VENDOR`: 28,206 nodes (Contractors / Suppliers)
  - `IDA`: 765 nodes (Implementing District Authorities)
  - **Total Nodes**: 29,745
- **Edge Types**:
  - `(MP, VENDOR)`: Direct financial disbursements (weight = total ₹, count = transactions)
  - `(VENDOR, IDA)`: Agency routing links (weight = total ₹, count = transactions)
  - `(MP, IDA)`: Administrative jurisdiction links (weight = total ₹, count = transactions)
  - **Total Edges**: 64,375

### 2. Bipartite MP-Vendor Graph ($G_{\text{Bipartite}}$)
- Strictly bipartite graph connecting MPs ($V_0$) to Vendors ($V_1$).
- Total Edges: 31,585 unique disbursement ties.
- Used for bipartite clique discovery and Louvain community detection.

## Graph Algorithms Implemented

| Algorithm | Method / Implementation | Purpose & Audit Interpretation |
|---|---|---|
| **PageRank Centrality** | $nx.pagerank(G, \alpha=0.85, \text{weight}='weight')$ | Identifies top influential hub contractors through whom disproportionate systemic fund flows circulate nationwide. |
| **Betweenness Centrality** | Core-subgraph sampled betweenness ($k=75$) | Identifies structural gatekeepers and bottleneck entities bridging disparate states or constituencies. |
| **Louvain Modularity Communities** | $nx.community.louvain\_communities(G_{\text{Bipartite}})$ | Discovers 310 tightly coupled clusters of MPs and contractors who exclusively transact together. |
| **Connected Components** | $nx.connected\_components(G)$ | Partitions network into 89 components; identifies the giant national component (97.8% of nodes) vs isolated regional islands. |
| **Bipartite Clique Detection** | Combinatorial co-occurrence mining | Detects multi-MP, multi-vendor complete subgraphs (bidding rings / cartels). |

## Empirical Network Findings on MPLADS
- **Total Network Scale**: 29,745 nodes, 64,375 edges
- **Macro-Component**: Giant component connects 29,103 nodes (**97.8%** of the entire network), demonstrating that MPLADS contractor networks are deeply interconnected across India.
- **Micro-Islands**: 88 isolated small components (representing remote constituencies with purely localized contractor bases).
- **Modularity**: 310 distinct communities discovered by Louvain optimization.
- **Top Hub Contractors by PageRank & Risk**:
  1. `SHARMA CONTRACTOR`: PageRank = $0.001381$ (Extensive multi-constituency footprint)
  2. `KRIDL BHUSIRI ACCOUNT WORKS`: PageRank = $0.001263$ (Active across 20 MPs and 17 IDAs)
  3. `TATA MOTORS`: PageRank = $0.001198$ (Institutional vehicle procurement)
  4. `SML ISUZU LTD`: PageRank = $0.000956$
  5. `FORCE MOTORS LIMITED`: PageRank = $0.000803$ (Active across 19 MPs and 9 States)

## Graph Visualization API (UI-Ready)
`MPLADSNetworkGraph.get_ego_subgraph(node_id, radius=1, max_neighbors=30)`:
Returns structured JSON data formatted specifically for frontend rendering engines (e.g. Cytoscape.js, React Flow, vis.js):
```json
{
  "nodes": [
    {"id": "MP:Ajay Bhatt", "label": "Ajay Bhatt", "type": "MP", "pagerank": 0.000412, "community": 42, "is_center": true},
    {"id": "VENDOR:SUNITA", "label": "SUNITA", "type": "VENDOR", "pagerank": 0.000155, "community": 42, "is_center": false}
  ],
  "edges": [
    {"source": "MP:Ajay Bhatt", "target": "VENDOR:SUNITA", "edge_type": "DISBURSEMENT", "weight": 4500000.0, "transactions": 4}
  ]
}
```

## Files
| File | Purpose |
|---|---|
| `backend/engine/network_graph.py` | `MPLADSNetworkGraph` class, heterogeneous builder, centralities, Louvain communities, ego subgraphs, and pipeline runner |
| `tests/test_network_graph.py` | 12-test comprehensive validation suite |

## Tests & Verification
12 unit tests covering:
- Graph node counts (774 MPs, 28,206 Vendors, 765 IDAs = 29,745 nodes) and edge counts
- Strict bipartite graph partition properties ($V_0 \leftrightarrow V_1$)
- Mathematical PageRank validation ($\sum PR = 1.0$, all values finite and non-negative)
- Betweenness score bounding in $[0.0, 1.0]$
- Connected component partitioning and giant component ratio (>95%)
- Louvain community detection across 310 modular clusters
- Retrieval of graph metrics for active, isolated (Chavan Vasantrao Balwantrao), and unknown MPs
- Ego-network extraction yielding valid JSON schema with node and edge attributes
- Detection of 50 bipartite contractor cliques
- Monotonic sorting of top hub contractors

## Test Results
**12/12 PASS** (2026-09-10)

## Definition of Done
✅ Heterogeneous multi-relational graph (MP ↔ Vendor ↔ IDA) constructed  
✅ Bipartite MP-Vendor projection and strict bipartiteness verified  
✅ PageRank and Betweenness centralities calculated with zero non-finite values  
✅ Louvain modularity community detection partitions the network into 310 clusters  
✅ Subgraph extraction API ready for React/Cytoscape visualization  
✅ 12/12 unit tests pass  
