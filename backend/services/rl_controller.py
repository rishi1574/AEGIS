import random
import copy
import math
from collections import defaultdict
from typing import List, Dict, Optional, Tuple


# ───────────────────────────────────────────────────────────
#  ATTACK PATTERN SIGNATURES — Blue Team detects by matching
#  transaction patterns, NOT by reading what the user clicked.
# ───────────────────────────────────────────────────────────
ATTACK_SIGNATURES = {
    "synthetic_id_bustout": {
        "signals": ["high_amount_zscore", "new_receiver", "rapid_velocity"],
        "description": "Burst of high-value txns to new receivers after dormancy",
    },
    "synthetic_id": {
        "signals": ["high_amount_zscore", "new_receiver", "rapid_velocity"],
        "description": "Burst of high-value txns to new receivers after dormancy",
    },
    "deepfake_ato": {
        "signals": ["new_device", "unusual_hour", "large_single_transfer"],
        "description": "Large P2P from new device at unusual hour",
    },
    "txn_fuzzing": {
        "signals": ["micro_variations", "same_merchant", "high_frequency"],
        "description": "Rapid small-variation probes to same merchant",
    },
    "digital_arrest": {
        "signals": ["large_single_transfer", "new_receiver", "unusual_hour"],
        "description": "Large scared transfer to unknown receiver",
    },
    "merchant_collusion": {
        "signals": ["high_fan_in", "no_repeat_customers", "uniform_amounts"],
        "description": "Many unique senders, no repeats, uniform amounts",
    },
    "vishing": {
        "signals": ["new_receiver", "large_single_transfer", "rapid_velocity"],
        "description": "Rapid large transfers after social engineering",
    },
    "pig_butchering": {
        "signals": ["escalating_amounts", "same_receiver", "long_buildup"],
        "description": "Slowly escalating amounts to same receiver",
    },
    "agentic_hijack": {
        "signals": ["new_device", "api_channel", "unusual_merchant"],
        "description": "Agent-initiated purchase to unusual merchant",
    },
    "model_poisoning": {
        "signals": ["borderline_amounts", "legitimate_pattern", "high_volume"],
        "description": "Flood of borderline-legitimate transactions",
    },
    "supply_chain_bec": {
        "signals": ["large_b2b", "new_receiver", "wire_transfer"],
        "description": "Large B2B wire to slightly modified vendor ID",
    },
    "api_exploit": {
        "signals": ["duplicate_amounts", "same_merchant", "millisecond_gap"],
        "description": "Near-duplicate transactions within milliseconds",
    },
    "adversarial_doc": {
        "signals": ["large_international", "wire_transfer", "new_receiver"],
        "description": "Large cross-border transfer with forged documents",
    },
    "adversarial_document": {
        "signals": ["large_international", "wire_transfer", "new_receiver"],
        "description": "Large cross-border transfer with forged documents",
    },
}

# Fallback for attack types not in the signatures dict
DEFAULT_SIGNATURE = {
    "signals": ["high_amount_zscore", "new_receiver", "unusual_hour"],
    "description": "Anomalous transaction pattern detected",
}


class QLearningPolicy:
    """
    Simple Q-table policy for Red Team mutation strategy.
    
    Tracks which mutation directions (increase/decrease amount, shift timing,
    add obfuscation) have been successful at evading detection, and reinforces
    those directions.
    """

    def __init__(self):
        # Q-values for each mutation dimension × direction
        # Dimensions: amount, velocity, route_obfuscation
        # Directions: increase (+1), decrease (-1), hold (0)
        self.q_table: Dict[str, Dict[str, float]] = {
            "amount": {"increase": 0.0, "decrease": 0.0, "hold": 0.0},
            "velocity": {"increase": 0.0, "decrease": 0.0, "hold": 0.0},
            "route": {"increase": 0.0, "decrease": 0.0, "hold": 0.0},
        }
        self.exploration_rate = 0.5
        self.learning_rate = 0.2
        self.last_actions: Dict[str, str] = {}  # dimension -> last action taken
        self.episode_rewards: List[float] = []  # track reward history

    def select_actions(self) -> Dict[str, str]:
        """Select mutation actions using epsilon-greedy policy."""
        actions = {}
        for dim in self.q_table:
            if random.random() < self.exploration_rate:
                # Explore: random action
                actions[dim] = random.choice(["increase", "decrease", "hold"])
            else:
                # Exploit: pick best Q-value action
                best_action = max(self.q_table[dim], key=self.q_table[dim].get)
                actions[dim] = best_action
        self.last_actions = actions
        return actions

    def update(self, reward: float):
        """Update Q-values based on reward for last actions taken."""
        self.episode_rewards.append(reward)
        for dim, action in self.last_actions.items():
            old_q = self.q_table[dim][action]
            # Simple temporal difference update
            self.q_table[dim][action] = old_q + self.learning_rate * (reward - old_q)

        # Decay exploration over time
        self.exploration_rate = max(0.05, self.exploration_rate * 0.95)

    def get_strategy_summary(self) -> str:
        """Human-readable summary of what the policy has learned."""
        preferred = {}
        for dim in self.q_table:
            best = max(self.q_table[dim], key=self.q_table[dim].get)
            val = self.q_table[dim][best]
            if val > 0.1:
                preferred[dim] = best
        if not preferred:
            return "Exploring random mutations..."
        parts = []
        if "amount" in preferred:
            parts.append(f"{'↑' if preferred['amount'] == 'increase' else '↓'} amount")
        if "velocity" in preferred:
            parts.append(f"{'↑' if preferred['velocity'] == 'increase' else '↓'} timing gaps")
        if "route" in preferred:
            parts.append(f"{'↑' if preferred['route'] == 'increase' else '↓'} obfuscation")
        return "Learned strategy: " + ", ".join(parts)


class BlueTeamAnalyzer:
    """
    Blue Team's pattern-based detection engine.
    
    Detects fraud by analyzing transaction patterns — NOT by reading what
    attack the user launched. It builds suspicion based on observable signals
    in the transaction data and gradually narrows down the attack type.
    """

    def __init__(self):
        self.suspicion_scores: Dict[str, float] = {}  # attack_type -> suspicion
        self.observed_signals: List[str] = []
        self.detection_threshold = 0.5
        self.sensitivity = 0.0  # grows as more patterns are detected
        self.detected_attack: Optional[str] = None
        self.detection_confidence = 0.0
        # Track what mutation dimensions have been successful against us
        self.known_evasion_tactics: Dict[str, float] = {
            "amount": 0.0,
            "velocity": 0.0,
            "route": 0.0,
        }

    def analyze_transaction(self, txn: dict) -> Tuple[bool, float, List[str]]:
        """
        Analyze a single transaction for fraud signals.
        Returns (is_suspicious, risk_score, signals_found).
        """
        signals = []
        risk = float(txn.get("risk_score", 0.5))
        amount = float(txn.get("amount_inr", 0))
        hour = int(txn.get("hour_of_day", 12)) if "hour_of_day" in txn else 12

        # Signal: high amount z-score
        zscore = float(txn.get("amount_zscore", 0))
        if abs(zscore) > 2.0 or amount > 50000:
            signals.append("high_amount_zscore")

        # Signal: new receiver
        if txn.get("is_new_receiver", False) or txn.get("is_new_receiver", 0) == 1:
            signals.append("new_receiver")

        # Signal: unusual hour (late night)
        if hour < 6 or hour > 22:
            signals.append("unusual_hour")

        # Signal: new device
        if txn.get("is_new_device", False) or txn.get("is_new_device", 0) == 1:
            signals.append("new_device")

        # Signal: rapid velocity
        velocity = float(txn.get("txn_count_last_1h", 0))
        if velocity > 5:
            signals.append("rapid_velocity")
            signals.append("high_frequency")

        # Signal: large single transfer
        if amount > 100000:
            signals.append("large_single_transfer")

        # Accumulate observed signals
        self.observed_signals.extend(signals)

        # Compute adjusted risk based on sensitivity
        effective_threshold = self.detection_threshold * (1.0 - self.sensitivity * 0.4)

        # Additional risk from known evasion tactic awareness
        evasion_awareness_boost = sum(self.known_evasion_tactics.values()) * 0.05
        adjusted_risk = min(1.0, risk + evasion_awareness_boost)

        is_caught = adjusted_risk > effective_threshold
        return is_caught, adjusted_risk, signals

    def update_suspicion(self, signals: List[str]):
        """Update suspicion scores based on observed signals — pattern matching."""
        for attack_type, sig_info in ATTACK_SIGNATURES.items():
            attack_signals = sig_info["signals"]
            # How many of the attack's signature signals match what we observed?
            match_count = sum(1 for s in attack_signals if s in signals)
            if match_count > 0:
                match_ratio = match_count / len(attack_signals)
                old_score = self.suspicion_scores.get(attack_type, 0.0)
                self.suspicion_scores[attack_type] = min(1.0, old_score + match_ratio * 0.15)

        # Determine top suspect
        if self.suspicion_scores:
            top_type = max(self.suspicion_scores, key=self.suspicion_scores.get)
            top_score = self.suspicion_scores[top_type]
            if top_score > 0.4:
                self.detected_attack = top_type
                self.detection_confidence = min(1.0, top_score)

    def adapt_to_evasion(self, mutation_params: Dict[str, float]):
        """Blue Team learns from Red Team's successful mutation tactics."""
        # If Red Team succeeded with amount manipulation, Blue Team learns to watch amounts more
        if abs(1.0 - mutation_params.get("amount_multiplier", 1.0)) > 0.15:
            self.known_evasion_tactics["amount"] = min(1.0,
                self.known_evasion_tactics["amount"] + 0.1)
        if mutation_params.get("velocity_shift_ms", 0) > 500:
            self.known_evasion_tactics["velocity"] = min(1.0,
                self.known_evasion_tactics["velocity"] + 0.1)
        if mutation_params.get("route_obfuscation", 0) > 0.3:
            self.known_evasion_tactics["route"] = min(1.0,
                self.known_evasion_tactics["route"] + 0.1)

        # Tighten threshold in response
        self.detection_threshold = max(0.25, self.detection_threshold - 0.02)

    def increase_sensitivity(self, amount: float = 0.06):
        """Gradually increase detection sensitivity as more data is observed."""
        self.sensitivity = min(0.95, self.sensitivity + amount)


class BattleSimulator:
    """
    Manages the full Red Team vs Blue Team adversarial battle simulation.

    The battle tells a story:
    1. RECON (ticks 1-5): Red injects fraud quietly. Blue monitors baseline.
       → Blue detects by PATTERN, not by knowing what was launched.
    2. DETECTION (ticks 6-15): Blue starts flagging suspicious patterns.
       → Gradually narrows down the attack type through signal matching.
    3. CONTAINMENT (ticks 16-25): Blue blocks most fraud. Red success drops.
    4. MUTATION (ticks 26-35): Red notices blocks, uses RL to mutate strategy.
       → Q-table tracks which mutations work. Some succeed.
    5. ADAPTATION (ticks 36-45): Blue adapts by learning what mutations worked.
       → Tightens defenses against the specific evasion tactics used.
    Then MUTATION→ADAPTATION cycles repeat with diminishing Red success.
    """

    def __init__(self):
        self.tick = 0
        self.current_attack: Optional[str] = None
        self.phase = "IDLE"

        # RL-driven Red Team policy
        self.red_policy = QLearningPolicy()
        self.mutation_params = {
            "amount_multiplier": 1.0,
            "velocity_shift_ms": 0,
            "route_obfuscation": 0.0,
        }
        self.mutation_generation = 0

        # Pattern-based Blue Team analyzer
        self.blue_analyzer = BlueTeamAnalyzer()

        # Battle stats
        self.red_team_total_attempts = 0
        self.red_team_evaded = 0
        self.red_team_success_rate = 0.0
        # Track recent window of attempts for smoother display
        self._recent_results: List[bool] = []  # True=evaded, False=caught
        self._recent_window = 20

        # Graph state — starts small, grows gradually
        self.graph_nodes: Dict[str, dict] = {}
        self.graph_edges: List[dict] = []
        self.max_nodes = 12  # Start with 12 nodes max
        self.node_age: Dict[str, int] = {}  # track when nodes were added

        # Instance log (the commentator table)
        self.instance_log: List[dict] = []

        # Accumulated commentary for the story
        self.commentary: List[str] = []

        # Battle history
        self.battle_history: List[dict] = []

        # Track mutation cycle number for oscillation
        self._current_cycle = 0
        self._last_phase = "IDLE"

    def reset(self, attack_type: str):
        """Reset battle state for a new attack."""
        self.__init__()
        self.current_attack = attack_type
        self.phase = "RECON"
        self.tick = 0

    def _advance_phase(self):
        """Determine current phase based on tick count and battle dynamics."""
        if self.current_attack is None:
            self.phase = "IDLE"
            return

        prev_phase = self._last_phase

        if self.tick <= 5:
            self.phase = "RECON"
        elif self.tick <= 15:
            self.phase = "DETECTION"
        elif self.tick <= 25:
            self.phase = "CONTAINMENT"
        else:
            # After containment, alternate MUTATION and ADAPTATION
            cycle_tick = (self.tick - 26) % 20
            if cycle_tick < 10:
                self.phase = "MUTATION"
            else:
                self.phase = "ADAPTATION"

        # Detect start of a NEW mutation cycle → Red gets a fresh surge
        if self.phase == "MUTATION" and prev_phase == "ADAPTATION":
            self._current_cycle += 1
            self._on_new_mutation_cycle()

        self._last_phase = self.phase

    def _on_new_mutation_cycle(self):
        """Called when Red Team enters a new MUTATION cycle after ADAPTATION.
        Partially resets Blue's defenses (simulating Blue overfitting to previous 
        mutation style) and gives Red a fresh strategy burst."""
        # Blue Team "overfits" — partial sensitivity decay (it focused on old pattern)
        self.blue_analyzer.sensitivity = max(
            0.3, self.blue_analyzer.sensitivity * 0.65)
        # Raise threshold slightly (Blue's specific counters become stale)
        self.blue_analyzer.detection_threshold = min(
            0.45, self.blue_analyzer.detection_threshold + 0.08)
        # Decay Blue's evasion tactic awareness (old tactics may not repeat)
        for k in self.blue_analyzer.known_evasion_tactics:
            self.blue_analyzer.known_evasion_tactics[k] *= 0.5

        # Red Team resets mutation params — trying fresh approach
        self.mutation_params = {
            "amount_multiplier": 1.0,
            "velocity_shift_ms": 0,
            "route_obfuscation": 0.0,
        }
        # Boost Red's exploration for this new cycle
        self.red_policy.exploration_rate = min(0.8, self.red_policy.exploration_rate + 0.3)

    def _manage_graph_capacity(self):
        """Grow the max node limit gradually and evict oldest nodes if over limit."""
        # Grow capacity slowly: +1 every 8 ticks, max 20
        if self.tick > 10 and self.tick % 8 == 0:
            self.max_nodes = min(20, self.max_nodes + 1)

        # Evict oldest nodes if over limit
        while len(self.graph_nodes) > self.max_nodes:
            if not self.node_age:
                break
            oldest_id = min(self.node_age, key=self.node_age.get)
            del self.graph_nodes[oldest_id]
            del self.node_age[oldest_id]

    def _add_node(self, node_id: str, ntype: str, risk: float, txn_count: int = 1):
        """Add or update a node in the graph with real stats."""
        short_id = node_id[-6:]
        if short_id not in self.graph_nodes:
            self.graph_nodes[short_id] = {
                "type": ntype,
                "risk": risk,
                "txn_count": txn_count,
                "blocked_count": 0,
            }
            self.node_age[short_id] = self.tick
        else:
            self.graph_nodes[short_id]["txn_count"] += 1
            self.graph_nodes[short_id]["risk"] = max(
                self.graph_nodes[short_id]["risk"], risk)

    def _mark_node_blocked(self, node_id: str):
        """Increment blocked count for a node."""
        short_id = node_id[-6:]
        if short_id in self.graph_nodes:
            self.graph_nodes[short_id]["blocked_count"] = \
                self.graph_nodes[short_id].get("blocked_count", 0) + 1

    def process_tick(self, fraud_transactions: List[dict],
                     normal_transactions: List[dict]) -> dict:
        """
        Process one simulation tick. Returns the full state for the frontend.
        """
        self.tick += 1
        self._advance_phase()
        self._manage_graph_capacity()

        tick_instances = []
        tick_edges = []
        red_msg = None
        blue_msg = None

        # ── Normal traffic (always flowing) ──
        for txn in normal_transactions[:2]:
            sender = str(txn.get("sender_id", ""))
            receiver = str(txn.get("receiver_id", ""))
            risk = float(txn.get("risk_score", 0.01))

            self._add_node(sender, "account", risk)
            self._add_node(receiver,
                           "merchant" if receiver.startswith("MER_") else "account",
                           risk)
            tick_edges.append({
                "source": sender[-6:],
                "target": receiver[-6:],
                "isFraud": False,
                "isFeedback": False,
                "amount": float(txn.get("amount_inr", 0)),
            })
            tick_instances.append({
                "txnId": str(txn.get("transaction_id", ""))[-8:],
                "attackVector": "Normal Traffic",
                "originalRisk": risk,
                "perturbedRisk": risk,
                "isEvaded": False,
                "phase": self.phase,
                "nodeRole": "—",
            })

        # ── Fraud traffic (phase-dependent) ──
        if self.phase == "RECON":
            red_msg, blue_msg, fraud_insts, fraud_edges = \
                self._phase_recon(fraud_transactions)
        elif self.phase == "DETECTION":
            red_msg, blue_msg, fraud_insts, fraud_edges = \
                self._phase_detection(fraud_transactions)
        elif self.phase == "CONTAINMENT":
            red_msg, blue_msg, fraud_insts, fraud_edges = \
                self._phase_containment(fraud_transactions)
        elif self.phase == "MUTATION":
            red_msg, blue_msg, fraud_insts, fraud_edges = \
                self._phase_mutation(fraud_transactions)
        elif self.phase == "ADAPTATION":
            red_msg, blue_msg, fraud_insts, fraud_edges = \
                self._phase_adaptation(fraud_transactions)
        else:
            fraud_insts, fraud_edges = [], []

        tick_instances.extend(fraud_insts)
        tick_edges.extend(fraud_edges)
        self.graph_edges = tick_edges
        self.instance_log = tick_instances

        # Track recent results from this tick's fraud instances
        for inst in fraud_insts:
            if inst.get("phase") not in ("IDLE",) and inst.get("attackVector") != "Normal Traffic":
                self._recent_results.append(inst.get("isEvaded", False))
        # Keep only last N results for a responsive window
        self._recent_results = self._recent_results[-self._recent_window:]

        # Calculate live metrics — use RECENT window for displayed rate
        if self.red_team_total_attempts > 0:
            self.red_team_success_rate = \
                self.red_team_evaded / self.red_team_total_attempts

        # Recent success rate (last N attempts) — more dynamic for charts
        recent_rate = self.red_team_success_rate
        if len(self._recent_results) > 0:
            recent_rate = sum(1 for r in self._recent_results if r) / len(self._recent_results)

        self.battle_history.append({
            "tick": self.tick,
            "phase": self.phase,
            "success_rate": recent_rate,
            "sensitivity": self.blue_analyzer.sensitivity,
            "detection_confidence": self.blue_analyzer.detection_confidence,
        })

        # Compute LIVE blue team metrics from battle performance
        # (not from the static model — these change with each tick)
        blue_accuracy = 1.0 - recent_rate
        blue_precision = max(0.5, blue_accuracy - 0.02) if self.tick > 5 else 0.5
        blue_recall = max(0.4, self.blue_analyzer.sensitivity) if self.tick > 5 else 0.5
        blue_f1 = (2 * blue_precision * blue_recall / (blue_precision + blue_recall)
                   if (blue_precision + blue_recall) > 0 else 0)
        blue_fpr = max(0, recent_rate * 0.3)  # False positive proxy

        return {
            "phase": self.phase,
            "tick": self.tick,
            "red_msg": red_msg,
            "blue_msg": blue_msg,
            "transaction_graph": {
                "nodes": [
                    {
                        "id": nid,
                        "type": info["type"],
                        "txn_count": info.get("txn_count", 0),
                        "risk": round(info.get("risk", 0), 3),
                        "blocked_count": info.get("blocked_count", 0),
                    }
                    for nid, info in self.graph_nodes.items()
                ],
                "edges": tick_edges,
            },
            "adversarial_instances": tick_instances,
            "detected_attack_type": self.blue_analyzer.detected_attack,
            "detection_confidence": round(self.blue_analyzer.detection_confidence, 2),
            "red_team_success_rate": round(recent_rate, 4),
            "blue_team_sensitivity": round(self.blue_analyzer.sensitivity, 4),
            "mutation_generation": self.mutation_generation,
            "mutation_params": {k: round(v, 3)
                                for k, v in self.mutation_params.items()},
            "live_blue_metrics": {
                "accuracy": round(blue_accuracy, 4),
                "precision": round(blue_precision, 4),
                "recall": round(blue_recall, 4),
                "f1_score": round(blue_f1, 4),
                "auc_roc": round(min(0.99, blue_accuracy + 0.02), 4),
                "false_positive_rate": round(blue_fpr, 4),
            },
        }

    # ──────────────────────────────────────────────
    # PHASE 1: RECON — Red Team injects covertly
    # Blue Team monitors, starts seeing signals
    # ──────────────────────────────────────────────
    def _phase_recon(self, fraud_txns: List[dict]) -> Tuple:
        instances = []
        edges = []

        # Red Team acts quietly — only inject 2 probes
        for txn in fraud_txns[:2]:
            sender = str(txn.get("sender_id", ""))
            receiver = str(txn.get("receiver_id", ""))
            risk = float(txn.get("risk_score", 0.8))

            self._add_node(sender, "mule", risk)
            self._add_node(receiver,
                           "merchant" if receiver.startswith("MER_") else "mule",
                           risk)

            # During recon, Blue Team hasn't raised sensitivity — fraud slips through
            self.red_team_total_attempts += 1
            self.red_team_evaded += 1

            # But Blue Team still observes signals (pattern detection)
            _, _, signals = self.blue_analyzer.analyze_transaction(txn)
            self.blue_analyzer.update_suspicion(signals)

            edges.append({
                "source": sender[-6:],
                "target": receiver[-6:],
                "isFraud": True,
                "isFeedback": False,
                "amount": float(txn.get("amount_inr", 0)),
            })
            instances.append({
                "txnId": str(txn.get("transaction_id", ""))[-8:],
                "attackVector": str(txn.get("fraud_type", "unknown")).replace("_", " ").title(),
                "originalRisk": risk,
                "perturbedRisk": risk,
                "isEvaded": True,
                "phase": "RECON",
                "nodeRole": f"Probe #{self.tick}: {sender[-6:]} → {receiver[-6:]}",
            })

        red_msg = f"Injecting covert probes ({len(fraud_txns[:2])} txns). " \
                  f"Staying under the radar..."
        blue_msg = "Monitoring baseline traffic. " \
                   f"Observing {len(self.blue_analyzer.observed_signals)} signals..."

        return red_msg, blue_msg, instances, edges

    # ──────────────────────────────────────────────
    # PHASE 2: DETECTION — Blue Team catches on
    # Detects by PATTERN, not by knowing the attack
    # ──────────────────────────────────────────────
    def _phase_detection(self, fraud_txns: List[dict]) -> Tuple:
        instances = []
        edges = []

        # Blue Team increases sensitivity each tick
        self.blue_analyzer.increase_sensitivity(0.08)

        caught_count = 0
        for txn in fraud_txns[:3]:
            sender = str(txn.get("sender_id", ""))
            receiver = str(txn.get("receiver_id", ""))
            risk = float(txn.get("risk_score", 0.8))

            self._add_node(sender, "mule", risk)
            self._add_node(receiver,
                           "merchant" if receiver.startswith("MER_") else "mule",
                           risk)

            # Blue Team analyzes using pattern matching
            is_caught, adjusted_risk, signals = \
                self.blue_analyzer.analyze_transaction(txn)
            self.blue_analyzer.update_suspicion(signals)

            self.red_team_total_attempts += 1
            if not is_caught:
                self.red_team_evaded += 1
            else:
                caught_count += 1
                self._mark_node_blocked(sender)

            edges.append({
                "source": sender[-6:],
                "target": receiver[-6:],
                "isFraud": True,
                "isFeedback": is_caught,
                "amount": float(txn.get("amount_inr", 0)),
            })

            detected_label = (
                self.blue_analyzer.detected_attack.replace("_", " ").title()
                if self.blue_analyzer.detected_attack else "Unknown Pattern"
            )
            instances.append({
                "txnId": str(txn.get("transaction_id", ""))[-8:],
                "attackVector": str(txn.get("fraud_type", "unknown")).replace("_", " ").title(),
                "originalRisk": risk,
                "perturbedRisk": adjusted_risk,
                "isEvaded": not is_caught,
                "phase": "DETECTION",
                "nodeRole": f"{'FLAGGED' if is_caught else 'Suspicious'}: "
                            f"{sender[-6:]}",
            })

        # Build detection message based on what Blue Team actually figured out
        if self.blue_analyzer.detected_attack:
            pattern_desc = ATTACK_SIGNATURES.get(
                self.blue_analyzer.detected_attack, DEFAULT_SIGNATURE
            )["description"]
            blue_msg = (
                f"Pattern match: {pattern_desc}. "
                f"Confidence: {self.blue_analyzer.detection_confidence*100:.0f}%. "
                f"Blocked {caught_count} txns."
            )
        else:
            blue_msg = (
                f"Anomalies flagged — {caught_count} suspicious txns. "
                f"Analyzing patterns... "
                f"({len(self.blue_analyzer.observed_signals)} signals collected)"
            )

        red_msg = (
            f"Continuing injection — {len(fraud_txns)} txns in pipeline. "
            f"Bypass rate: {self.red_team_success_rate*100:.0f}%"
        )

        return red_msg, blue_msg, instances, edges

    # ──────────────────────────────────────────────
    # PHASE 3: CONTAINMENT — Blue Team blocks most
    # ──────────────────────────────────────────────
    def _phase_containment(self, fraud_txns: List[dict]) -> Tuple:
        instances = []
        edges = []

        self.blue_analyzer.increase_sensitivity(0.05)

        caught_count = 0
        for txn in fraud_txns[:4]:
            sender = str(txn.get("sender_id", ""))
            receiver = str(txn.get("receiver_id", ""))
            risk = float(txn.get("risk_score", 0.8))

            self._add_node(sender, "mule", risk)
            self._add_node(receiver,
                           "merchant" if receiver.startswith("MER_") else "mule",
                           risk)

            is_caught, adjusted_risk, signals = \
                self.blue_analyzer.analyze_transaction(txn)
            self.blue_analyzer.update_suspicion(signals)

            self.red_team_total_attempts += 1
            if not is_caught:
                self.red_team_evaded += 1
            else:
                caught_count += 1
                self._mark_node_blocked(sender)

            edges.append({
                "source": sender[-6:],
                "target": receiver[-6:],
                "isFraud": True,
                "isFeedback": is_caught,
                "amount": float(txn.get("amount_inr", 0)),
            })
            instances.append({
                "txnId": str(txn.get("transaction_id", ""))[-8:],
                "attackVector": str(txn.get("fraud_type", "unknown")).replace("_", " ").title(),
                "originalRisk": risk,
                "perturbedRisk": adjusted_risk,
                "isEvaded": not is_caught,
                "phase": "CONTAINMENT",
                "nodeRole": f"{'BLOCKED' if is_caught else 'Slipped'}: "
                            f"{sender[-6:]}",
            })

        detected_label = (
            self.blue_analyzer.detected_attack.replace("_", " ").title()
            if self.blue_analyzer.detected_attack else "Unknown"
        )
        red_msg = (
            f"Success rate dropping to "
            f"{self.red_team_success_rate*100:.1f}%! "
            f"Preparing RL mutation strategy..."
        )
        blue_msg = (
            f"Containment active — {caught_count}/{len(fraud_txns[:4])} blocked. "
            f"Attack classified: {detected_label}. "
            f"Sensitivity: {self.blue_analyzer.sensitivity:.0%}"
        )

        return red_msg, blue_msg, instances, edges

    # ──────────────────────────────────────────────
    # PHASE 4: MUTATION — Red Team uses RL policy
    # to evolve attack parameters
    # ──────────────────────────────────────────────
    def _phase_mutation(self, fraud_txns: List[dict]) -> Tuple:
        instances = []
        edges = []

        self.mutation_generation += 1

        # Red Team selects mutation actions via Q-learning policy
        actions = self.red_policy.select_actions()

        # Apply mutations based on learned policy
        step_size = 0.15 + (self.mutation_generation * 0.05)  # escalate over time
        if actions["amount"] == "increase":
            self.mutation_params["amount_multiplier"] = min(3.0,
                self.mutation_params["amount_multiplier"] + step_size * 0.3)
        elif actions["amount"] == "decrease":
            self.mutation_params["amount_multiplier"] = max(0.1,
                self.mutation_params["amount_multiplier"] - step_size * 0.3)

        if actions["velocity"] == "increase":
            self.mutation_params["velocity_shift_ms"] = min(5000,
                self.mutation_params["velocity_shift_ms"] + int(step_size * 500))
        elif actions["velocity"] == "decrease":
            self.mutation_params["velocity_shift_ms"] = max(0,
                self.mutation_params["velocity_shift_ms"] - int(step_size * 300))

        if actions["route"] == "increase":
            self.mutation_params["route_obfuscation"] = min(1.0,
                self.mutation_params["route_obfuscation"] + step_size * 0.15)
        elif actions["route"] == "decrease":
            self.mutation_params["route_obfuscation"] = max(0.0,
                self.mutation_params["route_obfuscation"] - step_size * 0.1)

        evaded_count = 0
        caught_count = 0
        tick_rewards = []

        for txn in fraud_txns[:4]:
            sender = str(txn.get("sender_id", ""))
            receiver = str(txn.get("receiver_id", ""))
            original_risk = float(txn.get("risk_score", 0.8))

            # Apply mutation effect on risk score — mutations are powerful
            evasion_power = (
                abs(1.0 - self.mutation_params["amount_multiplier"]) * 0.4
                + self.mutation_params["route_obfuscation"] * 0.35
                + (self.mutation_params["velocity_shift_ms"] / 5000.0) * 0.25
            )
            perturbed_risk = max(0.01, original_risk - evasion_power)

            # Blue Team evaluates with pattern detection
            is_caught, _, signals = self.blue_analyzer.analyze_transaction(
                {**txn, "risk_score": perturbed_risk})

            self.red_team_total_attempts += 1
            reward = 0.0
            if not is_caught:
                self.red_team_evaded += 1
                evaded_count += 1
                reward = 1.0
            else:
                caught_count += 1
                self._mark_node_blocked(sender)
                reward = -1.0
            tick_rewards.append(reward)

            # RL Update: feed reward back to policy
            self.red_policy.update(reward)

            self._add_node(sender, "mule", perturbed_risk)
            self._add_node(receiver,
                           "merchant" if receiver.startswith("MER_") else "mule",
                           perturbed_risk)

            # Mutated amount for display
            mutated_amt = float(txn.get("amount_inr", 0)) * \
                self.mutation_params["amount_multiplier"]

            edges.append({
                "source": sender[-6:],
                "target": receiver[-6:],
                "isFraud": True,
                "isFeedback": is_caught,
                "amount": mutated_amt,
            })

            amt_label = f"×{self.mutation_params['amount_multiplier']:.1f}"
            vel_label = f"+{self.mutation_params['velocity_shift_ms']}ms"
            obf_label = f"{self.mutation_params['route_obfuscation']:.0%} obfusc"

            instances.append({
                "txnId": str(txn.get("transaction_id", ""))[-8:],
                "attackVector": f"Gen-{self.mutation_generation} "
                                f"({amt_label}, {vel_label})",
                "originalRisk": original_risk,
                "perturbedRisk": perturbed_risk,
                "isEvaded": not is_caught,
                "phase": "MUTATION",
                "nodeRole": f"{'EVADED' if not is_caught else 'CAUGHT'}: "
                            f"{sender[-6:]} [{obf_label}]",
            })

        strategy_summary = self.red_policy.get_strategy_summary()
        red_msg = (
            f"Mutation Gen-{self.mutation_generation}: "
            f"{strategy_summary}. "
            f"Result: {evaded_count} evaded, {caught_count} caught"
        )
        blue_msg = (
            f"New variant detected! Blocked {caught_count}/"
            f"{caught_count+evaded_count}. "
            f"Analyzing mutation pattern for countermeasures..."
        )

        return red_msg, blue_msg, instances, edges

    # ──────────────────────────────────────────────
    # PHASE 5: ADAPTATION — Blue Team counters
    # the specific mutations Red Team used
    # ──────────────────────────────────────────────
    def _phase_adaptation(self, fraud_txns: List[dict]) -> Tuple:
        instances = []
        edges = []

        # Blue Team adapts specifically to what worked for Red Team
        self.blue_analyzer.adapt_to_evasion(self.mutation_params)
        self.blue_analyzer.increase_sensitivity(0.04)

        caught_count = 0
        evaded_count = 0

        for txn in fraud_txns[:4]:
            sender = str(txn.get("sender_id", ""))
            receiver = str(txn.get("receiver_id", ""))
            original_risk = float(txn.get("risk_score", 0.8))

            # Red Team still using current mutations
            evasion_power = (
                abs(1.0 - self.mutation_params["amount_multiplier"]) * 0.4
                + self.mutation_params["route_obfuscation"] * 0.35
                + (self.mutation_params["velocity_shift_ms"] / 5000.0) * 0.25
            )
            perturbed_risk = max(0.01, original_risk - evasion_power)

            # Blue Team now adapted — uses its learned evasion awareness
            is_caught, adjusted_risk, signals = \
                self.blue_analyzer.analyze_transaction(
                    {**txn, "risk_score": perturbed_risk})

            self.red_team_total_attempts += 1
            if not is_caught:
                self.red_team_evaded += 1
                evaded_count += 1
                self.red_policy.update(1.0)
            else:
                caught_count += 1
                self._mark_node_blocked(sender)
                self.red_policy.update(-1.0)

            self._add_node(sender, "mule", adjusted_risk)
            self._add_node(receiver,
                           "merchant" if receiver.startswith("MER_") else "mule",
                           adjusted_risk)

            edges.append({
                "source": sender[-6:],
                "target": receiver[-6:],
                "isFraud": True,
                "isFeedback": is_caught,
                "amount": float(txn.get("amount_inr", 0)),
            })

            # Show what Blue Team learned about the evasion
            counter_info = []
            for dim, val in self.blue_analyzer.known_evasion_tactics.items():
                if val > 0.2:
                    counter_info.append(f"{dim}↑")
            counter_str = ", ".join(counter_info) if counter_info else "learning..."

            instances.append({
                "txnId": str(txn.get("transaction_id", ""))[-8:],
                "attackVector": f"Gen-{self.mutation_generation} (Adapted)",
                "originalRisk": original_risk,
                "perturbedRisk": adjusted_risk,
                "isEvaded": not is_caught,
                "phase": "ADAPTATION",
                "nodeRole": f"{'Evading' if not is_caught else 'Re-flagged'}: "
                            f"{sender[-6:]} [Blue: {counter_str}]",
            })

        red_msg = (
            f"Gen-{self.mutation_generation} being countered! "
            f"Success: {self.red_team_success_rate*100:.1f}%. "
            f"Need new strategy..."
        )
        blue_msg = (
            f"Adaptive countermeasures deployed. "
            f"Threshold: {self.blue_analyzer.detection_threshold:.2f}. "
            f"Blocked {caught_count}/{caught_count+evaded_count}. "
            f"Watching: {', '.join(k for k,v in self.blue_analyzer.known_evasion_tactics.items() if v > 0.2) or 'all dimensions'}"
        )

        return red_msg, blue_msg, instances, edges
