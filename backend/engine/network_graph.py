"""
NEXORAS — Module 8: NetworkX Graph Engine
=========================================
Heterogeneous and bipartite graph construction, topological centrality,
community detection, and network risk signal generation for MPLADS.

Entities (Nodes):
  - MP (Member of Parliament) [prefix: 'MP:']
  - Vendor (Contractor / Supplier) [prefix: 'VENDOR:']
  - IDA (Implementing District Authority) [prefix: 'IDA:']

Relationships (Edges):
  - (MP, Vendor): Financial disbursements (weight = sum of expenditure_amount)
  - (Vendor, IDA): Agency-routed payments (weight = sum of expenditure_amount)
  - (MP, IDA): Administrative jurisdiction / project execution

Graph Algorithms:
  - PageRank Centrality: Identifies systemic hub contractors and central MPs
  - Betweenness Centrality: Identifies bridging entities connecting disparate regions
  - Connected Components: Partitions network into macro and micro islands
  - Louvain Modularity Communities: Detects tightly coupled MP-Vendor clusters
  - Bipartite Cartel Discovery: Detects co-vendor partnerships and collusion rings
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx
import numpy as np
import pandas as pd


class MPLADSNetworkGraph:
    """
    NetworkX graph engine for modeling and analyzing complex relational
    structures across MPs, contractors, and district authorities.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

        # Graph representations
        self.G: nx.Graph = nx.Graph()  # Heterogeneous tripartite graph
        self.bipartite_mp_vendor: nx.Graph = nx.Graph()  # Direct MP <-> Vendor bipartite

        # Computed graph properties
        self.pagerank: Dict[str, float] = {}
        self.betweenness: Dict[str, float] = {}
        self.communities: List[Set[str]] = []
        self.node_community_map: Dict[str, int] = {}
        self.connected_components: List[Set[str]] = []

        # DataFrames for downstream consumption
        self.mp_graph_metrics_df: Optional[pd.DataFrame] = None
        self.vendor_graph_metrics_df: Optional[pd.DataFrame] = None

        self.is_built: bool = False

    def build(self, cleaned_datasets: Dict[str, pd.DataFrame]) -> "MPLADSNetworkGraph":
        """
        Construct heterogeneous and bipartite graphs from cleaned datasets.

        Parameters:
            cleaned_datasets: Dict containing 'expenditures' and 'mp_summary'.
        """
        exp = cleaned_datasets["expenditures"].copy()
        mp_sum = cleaned_datasets.get("mp_summary", pd.DataFrame()).copy()

        # Initialize graphs
        self.G.clear()
        self.bipartite_mp_vendor.clear()

        # 1. Add MP Nodes with metadata
        for _, r in mp_sum.iterrows():
            mp_id = f"MP:{r['mp_name']}"
            self.G.add_node(
                mp_id,
                node_type="MP",
                name=r["mp_name"],
                state=r.get("state", ""),
                constituency=r.get("constituency", ""),
                house=r.get("house", ""),
                allocated_amount=float(r.get("allocated_amount", 0.0)),
                total_expenditure=float(r.get("total_expenditure", 0.0)),
            )
            self.bipartite_mp_vendor.add_node(
                mp_id,
                bipartite=0,
                node_type="MP",
                name=r["mp_name"],
            )

        # 2. Aggregate MP-Vendor disbursements
        mp_v_edges = exp.groupby(["mp_name", "vendor"]).agg(
            total_amount=("expenditure_amount", "sum"),
            transaction_count=("expenditure_amount", "count"),
        ).reset_index()

        for _, r in mp_v_edges.iterrows():
            mp_id = f"MP:{r['mp_name']}"
            v_id = f"VENDOR:{r['vendor']}"
            amt = float(r["total_amount"])
            cnt = int(r["transaction_count"])

            # Ensure nodes exist
            if not self.G.has_node(v_id):
                self.G.add_node(v_id, node_type="VENDOR", name=r["vendor"])
            if not self.bipartite_mp_vendor.has_node(v_id):
                self.bipartite_mp_vendor.add_node(v_id, bipartite=1, node_type="VENDOR", name=r["vendor"])
            if not self.G.has_node(mp_id):
                self.G.add_node(mp_id, node_type="MP", name=r["mp_name"])
            if not self.bipartite_mp_vendor.has_node(mp_id):
                self.bipartite_mp_vendor.add_node(mp_id, bipartite=0, node_type="MP", name=r["mp_name"])

            # Add edges
            self.G.add_edge(mp_id, v_id, edge_type="DISBURSEMENT", weight=amt, transactions=cnt)
            self.bipartite_mp_vendor.add_edge(mp_id, v_id, weight=amt, transactions=cnt)

        # 3. Aggregate Vendor-IDA agency routing
        v_ida_edges = exp.groupby(["vendor", "ida"]).agg(
            total_amount=("expenditure_amount", "sum"),
            transaction_count=("expenditure_amount", "count"),
        ).reset_index()

        for _, r in v_ida_edges.iterrows():
            v_id = f"VENDOR:{r['vendor']}"
            ida_id = f"IDA:{r['ida']}"
            amt = float(r["total_amount"])
            cnt = int(r["transaction_count"])

            if not self.G.has_node(ida_id):
                self.G.add_node(ida_id, node_type="IDA", name=r["ida"])
            if not self.G.has_node(v_id):
                self.G.add_node(v_id, node_type="VENDOR", name=r["vendor"])

            self.G.add_edge(v_id, ida_id, edge_type="AGENCY_ROUTING", weight=amt, transactions=cnt)

        # 4. Aggregate MP-IDA administrative jurisdiction
        mp_ida_edges = exp.groupby(["mp_name", "ida"]).agg(
            total_amount=("expenditure_amount", "sum"),
            transaction_count=("expenditure_amount", "count"),
        ).reset_index()

        for _, r in mp_ida_edges.iterrows():
            mp_id = f"MP:{r['mp_name']}"
            ida_id = f"IDA:{r['ida']}"
            amt = float(r["total_amount"])
            cnt = int(r["transaction_count"])

            if not self.G.has_node(mp_id):
                self.G.add_node(mp_id, node_type="MP", name=r["mp_name"])
            if not self.G.has_node(ida_id):
                self.G.add_node(ida_id, node_type="IDA", name=r["ida"])

            self.G.add_edge(mp_id, ida_id, edge_type="ADMINISTRATIVE", weight=amt, transactions=cnt)

        # Step 5: Compute Centralities & Network Metrics
        self._compute_network_properties()
        self.is_built = True
        return self

    def _compute_network_properties(self) -> None:
        """Calculate PageRank, Betweenness, Components, and Louvain Communities."""
        # 1. PageRank on weighted heterogeneous graph
        self.pagerank = nx.pagerank(
            self.G,
            weight="weight",
            alpha=0.85,
            max_iter=100,
            tol=1e-6,
        )

        # 2. Connected Components
        self.connected_components = sorted(nx.connected_components(self.G), key=len, reverse=True)

        # 3. Louvain Community Detection (weighted)
        try:
            self.communities = nx.community.louvain_communities(
                self.bipartite_mp_vendor,
                weight="weight",
                seed=self.random_state,
            )
        except Exception:
            # Fallback to connected components if modularity optimization fails
            self.communities = [set(c) for c in self.connected_components]

        self.node_community_map = {}
        for comm_id, member_set in enumerate(self.communities):
            for node in member_set:
                self.node_community_map[node] = comm_id

        # 4. Betweenness Centrality on Core Subgraph (nodes with degree >= 2)
        # For scalability on 30k nodes, compute betweenness on the multi-connected core
        core_nodes = [n for n, d in self.G.degree() if d >= 2]
        if core_nodes:
            core_subgraph = self.G.subgraph(core_nodes)
            k_samples = min(75, len(core_nodes))
            core_betweenness = nx.betweenness_centrality(
                core_subgraph,
                k=k_samples,
                weight="weight",
                seed=self.random_state,
            )
            # Default to 0.0 for fringe leaf nodes
            self.betweenness = {n: core_betweenness.get(n, 0.0) for n in self.G.nodes()}
        else:
            self.betweenness = {n: 0.0 for n in self.G.nodes()}

        # 5. Build structured DataFrames
        self._build_metric_dataframes()

    def _build_metric_dataframes(self) -> None:
        """Construct analytical DataFrames for MPs and Vendors."""
        # --- MP Metrics ---
        mp_records = []
        for n, d in self.G.nodes(data=True):
            if d.get("node_type") == "MP":
                name = d.get("name", n.replace("MP:", ""))

                # Degree in bipartite graph = number of distinct vendors
                vendor_degree = self.bipartite_mp_vendor.degree(n) if self.bipartite_mp_vendor.has_node(n) else 0

                # Weighted spending from edges
                weighted_spend = 0.0
                if self.bipartite_mp_vendor.has_node(n):
                    weighted_spend = sum(data.get("weight", 0.0) for _, _, data in self.bipartite_mp_vendor.edges(n, data=True))

                pr = self.pagerank.get(n, 0.0)
                bc = self.betweenness.get(n, 0.0)
                comm = self.node_community_map.get(n, -1)

                mp_records.append({
                    "mp_name": name,
                    "graph_node_id": n,
                    "vendor_degree": int(vendor_degree),
                    "graph_weighted_spend": float(weighted_spend),
                    "graph_pagerank": float(pr),
                    "graph_betweenness": float(bc),
                    "community_id": int(comm),
                })

        mp_df = pd.DataFrame(mp_records)
        if not mp_df.empty:
            mp_df["pagerank_rank"] = mp_df["graph_pagerank"].rank(ascending=False, method="min").astype(int)
        self.mp_graph_metrics_df = mp_df

        # --- Vendor Metrics ---
        vendor_records = []
        for n, d in self.G.nodes(data=True):
            if d.get("node_type") == "VENDOR":
                name = d.get("name", n.replace("VENDOR:", ""))

                mp_degree = self.bipartite_mp_vendor.degree(n) if self.bipartite_mp_vendor.has_node(n) else 0

                weighted_payout = 0.0
                if self.bipartite_mp_vendor.has_node(n):
                    weighted_payout = sum(data.get("weight", 0.0) for _, _, data in self.bipartite_mp_vendor.edges(n, data=True))

                pr = self.pagerank.get(n, 0.0)
                bc = self.betweenness.get(n, 0.0)
                comm = self.node_community_map.get(n, -1)

                vendor_records.append({
                    "vendor": name,
                    "graph_node_id": n,
                    "mp_degree": int(mp_degree),
                    "graph_weighted_payout": float(weighted_payout),
                    "graph_pagerank": float(pr),
                    "graph_betweenness": float(bc),
                    "community_id": int(comm),
                })

        v_df = pd.DataFrame(vendor_records)
        if not v_df.empty:
            # Hub contractors: top 1% by PageRank
            pr_p99 = v_df["graph_pagerank"].quantile(0.99)
            v_df["is_hub_contractor"] = v_df["graph_pagerank"] >= pr_p99

            # Bridging contractors: top 1% by Betweenness
            bc_p99 = v_df["graph_betweenness"].quantile(0.99)
            v_df["is_bridging_contractor"] = (v_df["graph_betweenness"] >= bc_p99) & (v_df["graph_betweenness"] > 0)

            # Continuous network risk score (0-100)
            # Composite of multi-MP presence, PageRank, and betweenness
            norm_pr = (v_df["graph_pagerank"] / v_df["graph_pagerank"].max()) * 40.0
            norm_bc = (v_df["graph_betweenness"] / (v_df["graph_betweenness"].max() if v_df["graph_betweenness"].max() > 0 else 1.0)) * 30.0
            multi_mp_pts = np.clip((v_df["mp_degree"] - 1) * 10.0, 0.0, 30.0)

            net_risk = norm_pr + norm_bc + multi_mp_pts
            v_df["network_risk_score"] = np.round(np.clip(net_risk, 0.0, 100.0), 2)
            v_df.sort_values(["network_risk_score", "graph_weighted_payout"], ascending=[False, False], inplace=True)
            v_df.reset_index(drop=True, inplace=True)
            v_df["network_rank"] = np.arange(1, len(v_df) + 1)

        self.vendor_graph_metrics_df = v_df

    def get_mp_network_metrics(self, mp_name: str) -> Optional[Dict[str, Any]]:
        """Return graph centrality and cluster metrics for an MP."""
        if not self.is_built or self.mp_graph_metrics_df is None:
            raise RuntimeError("Graph must be built via build() before querying.")

        matches = self.mp_graph_metrics_df[self.mp_graph_metrics_df["mp_name"] == mp_name]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()

    def get_vendor_network_metrics(self, vendor_name: str) -> Optional[Dict[str, Any]]:
        """Return graph centrality, hub flags, and network rank for a vendor."""
        if not self.is_built or self.vendor_graph_metrics_df is None:
            raise RuntimeError("Graph must be built via build() before querying.")

        matches = self.vendor_graph_metrics_df[self.vendor_graph_metrics_df["vendor"] == vendor_name]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()

    def get_ego_subgraph(self, node_id: str, radius: int = 1, max_neighbors: int = 30) -> Dict[str, Any]:
        """
        Extract local ego network centered at node_id, formatted for Cytoscape / UI visualization.

        Returns:
            Dict with 'nodes': List[Dict] and 'edges': List[Dict].
        """
        if not self.is_built:
            raise RuntimeError("Graph must be built via build() before querying.")

        # Normalize prefix if needed
        target_node = node_id
        if not self.G.has_node(target_node):
            for prefix in ["MP:", "VENDOR:", "IDA:"]:
                if self.G.has_node(f"{prefix}{node_id}"):
                    target_node = f"{prefix}{node_id}"
                    break

        if not self.G.has_node(target_node):
            return {"nodes": [], "edges": []}

        # Collect 1-hop or 2-hop neighbors up to max_neighbors
        sub_nodes = {target_node}
        neighbors = list(self.G.neighbors(target_node))

        # Sort neighbors by edge weight descending to show top financial ties
        neighbors.sort(key=lambda n: self.G[target_node][n].get("weight", 0.0), reverse=True)
        sub_nodes.update(neighbors[:max_neighbors])

        subgraph = self.G.subgraph(sub_nodes)

        nodes_data = []
        for n in subgraph.nodes():
            d = subgraph.nodes[n]
            ntype = d.get("node_type", "UNKNOWN")
            nodes_data.append({
                "id": n,
                "label": d.get("name", n),
                "type": ntype,
                "pagerank": round(float(self.pagerank.get(n, 0.0)), 6),
                "community": int(self.node_community_map.get(n, -1)),
                "is_center": n == target_node,
            })

        edges_data = []
        for u, v, d in subgraph.edges(data=True):
            edges_data.append({
                "source": u,
                "target": v,
                "edge_type": d.get("edge_type", "DEFAULT"),
                "weight": float(d.get("weight", 0.0)),
                "transactions": int(d.get("transactions", 1)),
            })

        return {"nodes": nodes_data, "edges": edges_data}

    def get_top_hub_contractors(self, top_n: int = 20) -> pd.DataFrame:
        """Return the top influential hub contractors ranked by network influence."""
        if not self.is_built or self.vendor_graph_metrics_df is None:
            raise RuntimeError("Graph must be built via build() before querying.")
        return self.vendor_graph_metrics_df.head(top_n).copy()

    def get_bipartite_cliques(self, min_mps: int = 2, min_vendors: int = 2) -> List[Dict[str, Any]]:
        """
        Identify recurring bipartite clusters where multiple MPs share multiple identical vendors.
        These co-occurrence patterns indicate regional contractor consortiums.
        """
        if not self.is_built:
            raise RuntimeError("Graph must be built via build() before querying.")

        # Find vendors serving >= min_mps
        shared_vendors = [
            n for n, d in self.bipartite_mp_vendor.nodes(data=True)
            if d.get("node_type") == "VENDOR" and self.bipartite_mp_vendor.degree(n) >= min_mps
        ]

        cliques = []
        # Group MPs by the shared vendors they engage
        vendor_to_mps = {v: set(self.bipartite_mp_vendor.neighbors(v)) for v in shared_vendors}

        checked_pairs = set()
        for v1 in shared_vendors:
            for v2 in shared_vendors:
                if v1 >= v2:
                    continue
                pair_key = (v1, v2)
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)

                common_mps = vendor_to_mps[v1].intersection(vendor_to_mps[v2])
                if len(common_mps) >= min_mps:
                    cliques.append({
                        "vendors": [v1.replace("VENDOR:", ""), v2.replace("VENDOR:", "")],
                        "shared_mps": [mp.replace("MP:", "") for mp in common_mps],
                        "shared_mp_count": len(common_mps),
                    })

        # Sort cliques by shared MP count descending
        cliques.sort(key=lambda x: x["shared_mp_count"], reverse=True)
        return cliques[:50]

    def get_network_summary(self) -> Dict[str, Any]:
        """Return global topological metrics of the MPLADS network."""
        if not self.is_built:
            raise RuntimeError("Graph must be built via build() before querying.")

        node_types = nx.get_node_attributes(self.G, "node_type")
        mp_count = sum(1 for t in node_types.values() if t == "MP")
        vendor_count = sum(1 for t in node_types.values() if t == "VENDOR")
        ida_count = sum(1 for t in node_types.values() if t == "IDA")

        largest_comp_size = len(self.connected_components[0]) if self.connected_components else 0

        return {
            "total_nodes": int(self.G.number_of_nodes()),
            "total_edges": int(self.G.number_of_edges()),
            "mp_node_count": int(mp_count),
            "vendor_node_count": int(vendor_count),
            "ida_node_count": int(ida_count),
            "connected_components_count": int(len(self.connected_components)),
            "largest_component_size": int(largest_comp_size),
            "largest_component_ratio": float(largest_comp_size / self.G.number_of_nodes()) if self.G.number_of_nodes() > 0 else 0.0,
            "community_count": int(len(self.communities)),
            "bipartite_edges_count": int(self.bipartite_mp_vendor.number_of_edges()),
        }


def run_network_graph_pipeline(cleaned_datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Convenience runner executing Module 8 end-to-end pipeline.

    Returns:
        Dict containing:
          - 'network_engine': Fitted MPLADSNetworkGraph instance
          - 'mp_graph_metrics': pd.DataFrame of MP graph scores
          - 'vendor_graph_metrics': pd.DataFrame of vendor network scores
          - 'summary_stats': Dict of global network metrics
    """
    print("=" * 60)
    print("NEXORAS — Module 8: Running NetworkX Graph Engine Pipeline")
    print("=" * 60)
    engine = MPLADSNetworkGraph()
    engine.build(cleaned_datasets)
    stats = engine.get_network_summary()

    print(f"  Constructed Heterogeneous Graph: {stats['total_nodes']:,} nodes, {stats['total_edges']:,} edges")
    print(f"    - MPs: {stats['mp_node_count']:,} | Vendors: {stats['vendor_node_count']:,} | IDAs: {stats['ida_node_count']:,}")
    print(f"  Connected Components: {stats['connected_components_count']} (Largest Component: {stats['largest_component_size']:,} nodes, {stats['largest_component_ratio']:.1%})")
    print(f"  Louvain Modularity Communities: {stats['community_count']}")
    print("=" * 60)

    return {
        "network_engine": engine,
        "mp_graph_metrics": engine.mp_graph_metrics_df,
        "vendor_graph_metrics": engine.vendor_graph_metrics_df,
        "summary_stats": stats,
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
    from backend.ingestion.loader import load_all
    from backend.cleaning.cleaner import clean_all

    cleaned = clean_all(load_all())
    res = run_network_graph_pipeline(cleaned)
    top_hubs = res["network_engine"].get_top_hub_contractors(10)
    print("\nTop 10 Influential Hub Contractors (PageRank & Network Risk):")
    for _, r in top_hubs.iterrows():
        print(f"  Rank #{r['network_rank']}: {r['vendor']} | MP Degree: {r['mp_degree']} | PageRank: {r['graph_pagerank']:.6f} | Risk: {r['network_risk_score']:.1f}")
