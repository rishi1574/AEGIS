"""Graph-Based Anomaly Detector using NetworkX.

Builds a transaction graph and computes structural features that reveal:
- Money mule chains (rapid sequential transfers A→B→C→D)
- Synthetic identity clusters (many accounts, same device)
- Merchant collusion networks (high fan-in, no repeat customers)

Instead of a full GNN (which requires CUDA/PyG), we use NetworkX to compute
graph-theoretic features and feed them into the XGBoost model as additional
columns. This is computationally efficient and runs on any machine.
"""
import networkx as nx
import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple


class GraphAnomalyDetector:
    """Builds a transaction graph and computes per-account anomaly features."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.account_features: Dict[str, Dict] = {}
        self.device_graph = nx.Graph()  # Undirected: accounts sharing devices
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        """Build the transaction graph from a DataFrame."""
        print("Building transaction graph...")
        self.graph.clear()
        self.device_graph.clear()

        # Build directed money flow graph
        for _, row in df.iterrows():
            sender = str(row.get("sender_id", ""))
            receiver = str(row.get("receiver_id", ""))
            amount = float(row.get("amount_inr", 0))
            ts = row.get("timestamp", "")

            if sender and receiver:
                if self.graph.has_edge(sender, receiver):
                    self.graph[sender][receiver]["weight"] += amount
                    self.graph[sender][receiver]["count"] += 1
                else:
                    self.graph.add_edge(sender, receiver, weight=amount, count=1)

        # Build device sharing graph
        device_accounts = defaultdict(set)
        if "sender_device_id" in df.columns:
            for _, row in df.iterrows():
                dev = str(row.get("sender_device_id", ""))
                acc = str(row.get("sender_id", ""))
                if dev and acc:
                    device_accounts[dev].add(acc)

        for dev, accs in device_accounts.items():
            accs_list = list(accs)
            for i in range(len(accs_list)):
                for j in range(i + 1, len(accs_list)):
                    self.device_graph.add_edge(accs_list[i], accs_list[j])

        # Compute per-account features
        self._compute_features(df)
        self.is_fitted = True
        print(f"  Graph: {self.graph.number_of_nodes()} nodes, "
              f"{self.graph.number_of_edges()} edges")
        print(f"  Device sharing graph: {self.device_graph.number_of_nodes()} nodes, "
              f"{self.device_graph.number_of_edges()} edges")

    def _compute_features(self, df: pd.DataFrame):
        """Compute graph features for each account."""
        self.account_features = {}

        # PageRank — high centrality = potential mule hub
        try:
            pagerank = nx.pagerank(self.graph, max_iter=50, tol=1e-4)
        except Exception:
            pagerank = {}

        # In/Out degree
        in_deg = dict(self.graph.in_degree())
        out_deg = dict(self.graph.out_degree())

        # Compute per-account stats from raw data
        sender_stats = df.groupby("sender_id").agg(
            unique_receivers=("receiver_id", "nunique"),
            total_sent=("amount_inr", "sum"),
            txn_count=("amount_inr", "count"),
            avg_amount=("amount_inr", "mean"),
        ).to_dict("index")

        receiver_stats = df.groupby("receiver_id").agg(
            unique_senders=("sender_id", "nunique"),
            total_received=("amount_inr", "sum"),
            receive_count=("amount_inr", "count"),
        ).to_dict("index")

        all_accounts = set(df["sender_id"].unique()) | set(df["receiver_id"].unique())

        for acc in all_accounts:
            acc_str = str(acc)
            s_stats = sender_stats.get(acc, {})
            r_stats = receiver_stats.get(acc, {})

            # Fan-in / Fan-out ratio (collusion detection)
            fan_in = r_stats.get("unique_senders", 0)
            fan_out = s_stats.get("unique_receivers", 0)
            fan_ratio = fan_in / max(fan_out, 1)

            # Repeat rate: how many receivers/senders are repeated
            repeat_rate = 0
            if fan_out > 0:
                total_txns = s_stats.get("txn_count", 0)
                repeat_rate = 1.0 - (fan_out / max(total_txns, 1))

            # Device sharing degree (number of accounts sharing devices with this account)
            device_sharing_degree = (self.device_graph.degree(acc_str)
                                     if acc_str in self.device_graph else 0)

            # Local clustering coefficient in device graph
            device_clustering = 0.0
            if acc_str in self.device_graph and self.device_graph.degree(acc_str) > 1:
                try:
                    device_clustering = nx.clustering(self.device_graph, acc_str)
                except Exception:
                    pass

            self.account_features[acc] = {
                "graph_pagerank": pagerank.get(acc_str, 0.0),
                "graph_in_degree": in_deg.get(acc_str, 0),
                "graph_out_degree": out_deg.get(acc_str, 0),
                "graph_fan_in_ratio": fan_ratio,
                "graph_repeat_customer_rate": repeat_rate,
                "graph_device_sharing_degree": device_sharing_degree,
                "graph_device_clustering": device_clustering,
                "graph_total_received": r_stats.get("total_received", 0),
                "graph_unique_senders": fan_in,
            }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add graph features to a transaction DataFrame."""
        if not self.is_fitted:
            # Return zero features if not fitted
            graph_cols = ["graph_pagerank", "graph_in_degree", "graph_out_degree",
                          "graph_fan_in_ratio", "graph_repeat_customer_rate",
                          "graph_device_sharing_degree", "graph_device_clustering",
                          "graph_total_received", "graph_unique_senders"]
            for col in graph_cols:
                df[col] = 0.0
            return df

        # Map sender-level graph features to each transaction
        graph_features = []
        for _, row in df.iterrows():
            sender_id = row.get("sender_id", "")
            receiver_id = row.get("receiver_id", "")

            sender_feats = self.account_features.get(sender_id, {})
            receiver_feats = self.account_features.get(receiver_id, {})

            combined = {
                "graph_pagerank": sender_feats.get("graph_pagerank", 0),
                "graph_in_degree": sender_feats.get("graph_in_degree", 0),
                "graph_out_degree": sender_feats.get("graph_out_degree", 0),
                "graph_fan_in_ratio": receiver_feats.get("graph_fan_in_ratio", 0),
                "graph_repeat_customer_rate": receiver_feats.get("graph_repeat_customer_rate", 0),
                "graph_device_sharing_degree": sender_feats.get("graph_device_sharing_degree", 0),
                "graph_device_clustering": sender_feats.get("graph_device_clustering", 0),
                "graph_total_received": receiver_feats.get("graph_total_received", 0),
                "graph_unique_senders": receiver_feats.get("graph_unique_senders", 0),
            }
            graph_features.append(combined)

        graph_df = pd.DataFrame(graph_features, index=df.index)
        return pd.concat([df, graph_df], axis=1)

    def get_mule_chain_candidates(self, min_chain_length: int = 3) -> List[List[str]]:
        """Find potential mule chains (rapid sequential paths)."""
        chains = []
        # Find paths of length >= min_chain_length with high flow
        for node in self.graph.nodes():
            for target in self.graph.nodes():
                if node != target:
                    try:
                        paths = list(nx.all_simple_paths(
                            self.graph, node, target,
                            cutoff=min_chain_length + 1))
                        for path in paths:
                            if len(path) >= min_chain_length:
                                chains.append(path)
                        if len(chains) > 100:  # Cap for performance
                            return chains
                    except nx.NetworkXError:
                        continue
        return chains
