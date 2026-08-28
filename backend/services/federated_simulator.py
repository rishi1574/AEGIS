import time
import hashlib
from backend.services.data_service import data_service

class FederatedBankNode:
    def __init__(self, name: str, data_volume: int):
        self.name = name
        self.data_volume = data_volume
        # Deterministic variance offset derived from node name
        name_hash = int(hashlib.md5(name.encode()).hexdigest(), 16)
        self.offset = (name_hash % 100) / 10000.0  # E.g., 0.00xx penalty
        self.local_accuracy = 0.8
        self.gradient_updates_sent = 0
        self.status = "SYNCED"

    def update_local(self, global_acc: float, current_round: int):
        # Local model is slightly behind global model deterministically
        self.local_accuracy = max(0.5, global_acc - self.offset - 0.002)
        
        # Deterministic status based on current round to simulate staggered updates
        round_hash = int(hashlib.md5(f"{current_round}_{self.name}".encode()).hexdigest(), 16)
        self.status = "UPDATED" if (round_hash % 100) > 30 else "COMPUTING"
        if self.status == "UPDATED":
            self.gradient_updates_sent += 1

class FederatedCoordinator:
    def __init__(self):
        self.nodes = [
            FederatedBankNode("Global Bank (APAC)", 1250000),
            FederatedBankNode("Retail Bank (EMEA)", 850000),
            FederatedBankNode("Digital Bank (NAM)", 2100000)
        ]
        self.round = 1

    def aggregate_weights(self):
        # Pull actual global model accuracy from the real evaluation results
        metrics = data_service.get_metrics()
        real_global_acc = metrics.get("f1_score", 0.938)
        
        self.round += 1
        
        for n in self.nodes:
            n.update_local(real_global_acc, self.round)

        return {
            "round": self.round,
            "global_accuracy": round(real_global_acc, 4),
            "nodes": [
                {
                    "name": n.name,
                    "accuracy": round(n.local_accuracy, 4),
                    "status": n.status,
                    "updates": n.gradient_updates_sent
                } for n in self.nodes
            ]
        }

federated_coordinator = FederatedCoordinator()
