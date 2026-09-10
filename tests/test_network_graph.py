"""
NEXORAS — Module 8 Test Suite: NetworkX Graph Engine
===================================================
Verifies heterogeneous graph construction, PageRank, betweenness,
connected components, Louvain modularity communities, ego-subgraphs,
and bipartite cartel cluster detection.
"""

import io
import os
import sys
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# UTF-8 stdout wrapper for Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from backend.ingestion.loader import load_all
from backend.cleaning.cleaner import clean_all
from backend.engine.network_graph import (
    MPLADSNetworkGraph,
    run_network_graph_pipeline,
)


class TestNetworkGraphEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run data loading, cleaning, and graph construction once."""
        raw_data = load_all()
        cls.cleaned_data = clean_all(raw_data)
        cls.engine = MPLADSNetworkGraph(random_state=42)
        cls.engine.build(cls.cleaned_data)
        cls.summary = cls.engine.get_network_summary()

    def test_01_graph_construction_counts(self):
        """Test node and edge counts in heterogeneous graph."""
        summary = self.summary
        self.assertGreater(summary["total_nodes"], 29000)
        self.assertEqual(summary["mp_node_count"], 774)
        self.assertEqual(summary["vendor_node_count"], 28206)
        self.assertGreaterEqual(summary["ida_node_count"], 700)
        self.assertGreater(summary["total_edges"], 30000)
        self.assertGreater(summary["bipartite_edges_count"], 30000)
        print(f"  PASS: Heterogeneous graph built with {summary['total_nodes']:,} nodes & {summary['total_edges']:,} edges")

    def test_02_bipartite_structure(self):
        """Test bipartite MP-Vendor graph integrity."""
        bg = self.engine.bipartite_mp_vendor
        self.assertIsNotNone(bg)

        # Ensure all nodes have bipartite attribute 0 (MP) or 1 (Vendor)
        for n, d in bg.nodes(data=True):
            self.assertIn(d.get("bipartite"), [0, 1], f"Node {n} missing bipartite tag")

        # Every edge must connect bipartite 0 to bipartite 1
        for u, v in bg.edges():
            u_part = bg.nodes[u]["bipartite"]
            v_part = bg.nodes[v]["bipartite"]
            self.assertNotEqual(u_part, v_part, f"Edge ({u}, {v}) connects same partition")
        print("  PASS: Bipartite MP-Vendor graph satisfies strict bipartite criteria")

    def test_03_pagerank_properties(self):
        """Test that PageRank sums to 1.0 and is finite."""
        pr = self.engine.pagerank
        self.assertEqual(len(pr), self.summary["total_nodes"])

        pr_values = list(pr.values())
        self.assertTrue(all(np.isfinite(v) for v in pr_values))
        self.assertTrue(all(v >= 0.0 for v in pr_values))

        # PageRank sum should equal 1.0
        self.assertAlmostEqual(sum(pr_values), 1.0, places=4)

        # Prominent vendors should have top PageRank
        top_hubs = self.engine.get_top_hub_contractors(10)
        self.assertFalse(top_hubs.empty)
        self.assertGreater(top_hubs.iloc[0]["graph_pagerank"], top_hubs.iloc[-1]["graph_pagerank"])
        print(f"  PASS: PageRank sums to {sum(pr_values):.4f} with zero non-finite values")

    def test_04_betweenness_properties(self):
        """Test betweenness centrality calculations."""
        bc = self.engine.betweenness
        self.assertEqual(len(bc), self.summary["total_nodes"])

        bc_values = list(bc.values())
        self.assertTrue(all(np.isfinite(v) for v in bc_values))
        self.assertTrue(all(v >= 0.0 for v in bc_values))
        self.assertTrue(all(v <= 1.0 for v in bc_values))
        print("  PASS: Betweenness centrality scores are bounded in [0.0, 1.0]")

    def test_05_connected_components(self):
        """Test connected components distribution."""
        comps = self.engine.connected_components
        self.assertGreater(len(comps), 0)

        # Partition check: sum of component sizes equals total nodes
        total_in_comps = sum(len(c) for c in comps)
        self.assertEqual(total_in_comps, self.summary["total_nodes"])

        # Largest component should contain majority of nodes (>80%)
        self.assertGreater(self.summary["largest_component_ratio"], 0.80)
        print(f"  PASS: Network partitions into {len(comps)} components; giant component contains {self.summary['largest_component_ratio']:.1%} of nodes")

    def test_06_louvain_communities(self):
        """Test community detection in bipartite network."""
        communities = self.engine.communities
        self.assertGreater(len(communities), 10)

        # Every node in node_community_map should have non-negative community ID
        comm_map = self.engine.node_community_map
        self.assertGreater(len(comm_map), 0)
        for node, comm_id in comm_map.items():
            self.assertGreaterEqual(comm_id, 0)
        print(f"  PASS: Discovered {len(communities)} modular communities")

    def test_07_mp_network_metrics(self):
        """Test MP network metrics extraction."""
        # Standard MP
        sample_mp = self.cleaned_data["expenditures"]["mp_name"].iloc[0]
        mp_metrics = self.engine.get_mp_network_metrics(sample_mp)
        self.assertIsNotNone(mp_metrics)
        self.assertEqual(mp_metrics["mp_name"], sample_mp)
        self.assertGreater(mp_metrics["vendor_degree"], 0)
        self.assertGreater(mp_metrics["graph_weighted_spend"], 0.0)
        self.assertGreater(mp_metrics["graph_pagerank"], 0.0)
        self.assertGreaterEqual(mp_metrics["community_id"], 0)

        # Zero expenditure MP (CHAVAN VASANTRAO BALWANTRAO)
        zero_mp = self.engine.get_mp_network_metrics("CHAVAN VASANTRAO BALWANTRAO")
        self.assertIsNotNone(zero_mp)
        self.assertEqual(zero_mp["vendor_degree"], 0)
        self.assertEqual(zero_mp["graph_weighted_spend"], 0.0)

        # Unknown MP
        self.assertIsNone(self.engine.get_mp_network_metrics("UNKNOWN_MP_XYZ"))
        print("  PASS: MP network metrics retrieved for active, isolated, and unknown MPs")

    def test_08_vendor_network_metrics(self):
        """Test vendor network metrics and ranking."""
        sample_v = "FORCE MOTORS LIMITED"
        v_metrics = self.engine.get_vendor_network_metrics(sample_v)
        self.assertIsNotNone(v_metrics)
        self.assertEqual(v_metrics["vendor"], sample_v)
        self.assertGreaterEqual(v_metrics["mp_degree"], 10)
        self.assertGreater(v_metrics["graph_pagerank"], 0.0)
        self.assertGreater(v_metrics["network_risk_score"], 0.0)
        self.assertLessEqual(v_metrics["network_risk_score"], 100.0)

        # Unknown vendor
        self.assertIsNone(self.engine.get_vendor_network_metrics("UNKNOWN_VENDOR_XYZ"))
        print("  PASS: Vendor network metrics verified for high-degree contractors")

    def test_09_ego_subgraph_visualization(self):
        """Test ego subgraph extraction for UI rendering."""
        # Query MP ego graph
        sample_mp = self.cleaned_data["expenditures"]["mp_name"].iloc[0]
        ego = self.engine.get_ego_subgraph(sample_mp, radius=1, max_neighbors=15)
        self.assertIn("nodes", ego)
        self.assertIn("edges", ego)
        self.assertGreater(len(ego["nodes"]), 0)
        self.assertGreater(len(ego["edges"]), 0)

        # Check node schema
        first_node = ego["nodes"][0]
        for key in ["id", "label", "type", "pagerank", "community", "is_center"]:
            self.assertIn(key, first_node)

        # Check edge schema
        first_edge = ego["edges"][0]
        for key in ["source", "target", "edge_type", "weight", "transactions"]:
            self.assertIn(key, first_edge)

        # Unknown node returns empty structures
        empty_ego = self.engine.get_ego_subgraph("NON_EXISTENT_ENTITY")
        self.assertEqual(empty_ego["nodes"], [])
        self.assertEqual(empty_ego["edges"], [])
        print("  PASS: Ego subgraph API exports valid Cytoscape/UI JSON structures")

    def test_10_bipartite_clique_detection(self):
        """Test detection of shared contractor consortiums."""
        cliques = self.engine.get_bipartite_cliques(min_mps=2, min_vendors=2)
        self.assertIsInstance(cliques, list)
        self.assertGreater(len(cliques), 0)

        # Check structure
        first_clique = cliques[0]
        self.assertIn("vendors", first_clique)
        self.assertIn("shared_mps", first_clique)
        self.assertIn("shared_mp_count", first_clique)
        self.assertEqual(len(first_clique["vendors"]), 2)
        self.assertGreaterEqual(first_clique["shared_mp_count"], 2)
        print(f"  PASS: Detected {len(cliques)} bipartite contractor cliques")

    def test_11_top_hub_contractors(self):
        """Test top hub contractors extraction."""
        top20 = self.engine.get_top_hub_contractors(20)
        self.assertEqual(len(top20), 20)
        self.assertEqual(top20.iloc[0]["network_rank"], 1)

        # Scores should be descending
        self.assertTrue(top20["network_risk_score"].is_monotonic_decreasing)
        print("  PASS: Top hub contractors ordered strictly by network risk")

    def test_12_pipeline_runner(self):
        """Test convenience pipeline runner."""
        res = run_network_graph_pipeline(self.cleaned_data)
        self.assertIn("network_engine", res)
        self.assertIn("mp_graph_metrics", res)
        self.assertIn("vendor_graph_metrics", res)
        self.assertIn("summary_stats", res)
        self.assertGreater(len(res["mp_graph_metrics"]), 0)
        self.assertGreater(len(res["vendor_graph_metrics"]), 0)
        print("  PASS: run_network_graph_pipeline executes end-to-end")


if __name__ == "__main__":
    print("=" * 60)
    print("NEXORAS — Module 8 Test Suite (NetworkX Graph Engine)")
    print("=" * 60)
    unittest.main(verbosity=2)
