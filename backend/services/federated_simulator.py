import random
import time
import asyncio

class FederatedBankNode:
    def __init__(self, name: str, data_volume: int):
        self.name = name
        self.data_volume = data_volume
        self.local_accuracy = random.uniform(0.70, 0.85)
        self.gradient_updates_sent = 0
        self.status = "SYNCING"

    def train_local(self, new_attacks_detected: int):
        # Simulate local learning on new attacks
        improvement = random.uniform(0.001, 0.015) * (new_attacks_detected / 10.0)
        self.local_accuracy = min(0.99, self.local_accuracy + improvement)
        self.gradient_updates_sent += 1
        return {
            "name": self.name,
            "accuracy": round(self.local_accuracy, 4),
            "gradients": self.gradient_updates_sent,
            "status": "UPDATED" if random.random() > 0.3 else "COMPUTING"
        }

class FederatedCoordinator:
    def __init__(self):
        self.nodes = [
            FederatedBankNode("Global Bank (APAC)", 1250000),
            FederatedBankNode("Retail Bank (EMEA)", 850000),
            FederatedBankNode("Digital Bank (NAM)", 2100000)
        ]
        self.global_model_accuracy = 0.88
        self.round = 1

    def aggregate_weights(self):
        # Federated Averaging (FedAvg) simulation
        total_volume = sum(n.data_volume for n in self.nodes)
        weighted_acc = sum(n.local_accuracy * (n.data_volume / total_volume) for n in self.nodes)
        
        # The global model benefits from the ensemble effect, adding a small boost
        self.global_model_accuracy = min(0.998, weighted_acc + 0.02)
        self.round += 1
        
        # Propagate back to nodes
        for n in self.nodes:
            n.local_accuracy = min(0.99, self.global_model_accuracy - random.uniform(0.005, 0.015))
            n.status = "SYNCED"

        return {
            "round": self.round,
            "global_accuracy": round(self.global_model_accuracy, 4),
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
