# VANGUARD Architecture

## Components
1. **Red Team (Attack Simulator):** Uses `TransactionGenerator` seeded with Gymnasium RL environments to create novel zero-day attacks.
2. **Blue Team (Defense Pipeline):** A meta-ensemble model combining:
   - XGBoost (Tabular features)
   - Temporal Transformers (Sequence anomalies)
   - Heterogeneous GNNs (Mule graph detection)
3. **War Room (Frontend):** Next.js dashboard providing real-time telemetry on the adversarial loop.
4. **Backend (FastAPI):** Orchestrates the simulation and serves model inferences via WebSocket.
