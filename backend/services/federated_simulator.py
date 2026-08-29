import time
import hashlib
import random
from backend.services.data_service import data_service


class FederatedBankNode:
    def __init__(self, name: str, region: str, base_strength: float):
        self.name = name
        self.region = region
        self.base_strength = base_strength
        # Deterministic variance offset derived from node name
        name_hash = int(hashlib.md5(name.encode()).hexdigest(), 16)
        self.offset = (name_hash % 100) / 10000.0
        self.local_accuracy = base_strength
        self.gradient_updates_sent = 0
        self.status = "SYNCED"

    def update_local(self, global_acc: float, current_round: int, bypass_rate: float):
        """Update local model accuracy based on the current battle state."""
        # Local banks have different exposure to the attack
        # APAC sees it first, EMEA lags, NAM benefits from federated learning
        attack_impact = bypass_rate * random.uniform(0.08, 0.15)
        self.local_accuracy = max(0.60,
            global_acc - self.offset - attack_impact)
        
        # Some natural jitter for realism
        self.local_accuracy += random.uniform(-0.01, 0.01)
        self.local_accuracy = min(0.99, max(0.55, self.local_accuracy))

        # Deterministic status based on round
        round_hash = int(hashlib.md5(
            f"{current_round}_{self.name}".encode()).hexdigest(), 16)
        self.status = "UPDATED" if (round_hash % 100) > 30 else "COMPUTING"
        if self.status == "UPDATED":
            self.gradient_updates_sent += 1


class FederatedCoordinator:
    def __init__(self):
        self.nodes = [
            FederatedBankNode("Global Bank (APAC)", "APAC", 0.82),
            FederatedBankNode("Retail Bank (EMEA)", "EMEA", 0.79),
            FederatedBankNode("Digital Bank (NAM)", "NAM", 0.84),
        ]
        self.round = 1

    def aggregate_weights(self, current_bypass_rate: float = 0.0):
        """Aggregate federated weights. Uses the live bypass rate to create
        realistic variation — when attacks succeed, bank accuracy drops."""
        # Cap rounds at reasonable number (resets each simulation)
        self.round = min(self.round + 1, 30)

        # Global accuracy is derived from how well the system is doing
        # If bypass_rate is high (Red winning), accuracy drops
        global_acc = max(0.70, min(0.98, 1.0 - current_bypass_rate * 1.5))
        
        for n in self.nodes:
            n.update_local(global_acc, self.round, current_bypass_rate)

        # Federated improvement: global model is better than individual banks
        avg_local = sum(n.local_accuracy for n in self.nodes) / len(self.nodes)
        federated_f1 = min(0.99, avg_local + 0.05 + random.uniform(0.01, 0.03))
        improvement = ((federated_f1 - avg_local) / avg_local) * 100

        return {
            "round": self.round,
            "global_accuracy": round(federated_f1, 4),
            "nodes": [
                {
                    "name": n.name,
                    "accuracy": round(n.local_accuracy, 4),
                    "status": n.status,
                    "updates": n.gradient_updates_sent,
                } for n in self.nodes
            ],
            "improvement": f"+{improvement:.1f}%",
        }


federated_coordinator = FederatedCoordinator()
