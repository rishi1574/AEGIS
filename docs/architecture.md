# AEGIS Architecture

## Components
1. **Red Team (Attack Simulator):** Uses `TransactionGenerator` seeded with Gymnasium RL environments to create novel zero-day attacks.
2. **Blue Team (Defense Pipeline):** A meta-ensemble model combining:
   - XGBoost (Tabular features)
   - Temporal Transformers (Sequence anomalies)
   - Heterogeneous GNNs (Mule graph detection)
3. **War Room (Frontend):** Next.js dashboard providing real-time telemetry on the adversarial loop.
4. **Backend (FastAPI):** Orchestrates the simulation and serves model inferences via per-session WebSocket connections.

## Backend Session Architecture
Each user connecting to the War Room receives an independent, isolated session:
- **Per-session `BattleSimulator`** — Every WebSocket connection gets its own RL-driven Red Team vs Blue Team battle instance.
- **Per-session telemetry** — The background telemetry loop sends each session its own private data feed computed from its own battle state.
- **Session isolation** — User A launching an attack has zero effect on User B's dashboard. Both run fully independent adversarial simulations.
- **Shared read-only data** — The underlying transaction dataset and trained model artifacts are loaded once at startup and shared across sessions (read-only).

## Battle Simulation Phases
The `BattleSimulator` (in `rl_controller.py`) drives a 5-phase adversarial narrative per session:
1. **RECON** (ticks 1–5): Red Team injects covert probes. Blue Team monitors baseline.
2. **DETECTION** (ticks 6–15): Blue Team starts flagging suspicious patterns by signal matching.
3. **CONTAINMENT** (ticks 16–25): Blue Team blocks most fraud. Red Team success rate drops.
4. **MUTATION** (ticks 26–35): Red Team uses Q-learning RL policy to evolve attack parameters.
5. **ADAPTATION** (ticks 36–45): Blue Team adapts by learning which mutations worked.

After ADAPTATION, the cycle returns to MUTATION with a fresh Red Team strategy burst, creating an ongoing adversarial co-evolution loop.
