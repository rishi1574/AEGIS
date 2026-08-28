# 📊 Member C — Data/Research Lead & Strategist: Complete Guide

> **Role:** Write the Pitch Deck, define the VANGUARD USPs, explain the AI models (GNN, SHAP, Federated), and curate the training datasets.
> **Your directories:** `docs/`, `data/`
> **Do NOT touch:** `frontend/`, `backend/`, `red_team/` code
> **Goal:** Prove to Mastercard that this is the best, most technically sound, and most innovative solution for 2026.

---

## 1. The Core Narrative (Pitch Deck Outline)

You need to create a 10-15 slide pitch deck. Here is the exact structure and content to include.

**Slide 1: Title & Hook**
*   **Title:** Project VANGUARD (Adversarial Evolution & Generative Intelligence Shield)
*   **Subtitle:** Self-Healing Payment Security for the GenAI Era.
*   **Hook:** By 2026, fraudsters aren't writing rules; they are using Agentic AI to probe networks at machine speed. Static defenses are obsolete. VANGUARD fights AI with AI.

**Slide 2: The Problem (GenAI Fraud Landscape 2026)**
*   **Speed:** Agentic Hijacking (AI agents making autonomous purchases).
*   **Scale:** Transaction Fuzzing (millions of micro-mutations to bypass thresholds).
*   **Sophistication:** Deepfake ATOs & Synthetic ID Bust-Outs.
*   **The Flaw:** Current models (even ML) suffer from *Concept Drift*. They degrade as fraud evolves.

**Slide 3: The VANGUARD Solution (Red vs. Blue)**
*   **Concept:** A continuous, closed-loop adversarial simulation.
*   **Red Team Engine:** Autonomous AI agents generating novel fraud vectors (not just historical replays).
*   **Blue Team Engine:** Real-time detection pipeline learning from the Red Team's zero-day attacks.
*   **Result:** A self-healing defense system that patches vulnerabilities *before* they are exploited in the wild.

**Slide 4: Architecture Overview**
*   *Include a diagram here showing:*
    *   **Data Generation:** Personas (Student, Merchant, Mule) interacting.
    *   **Red Team:** Injecting 12 specific fraud types (Vishing, AP4M abuse, etc.).
    *   **Blue Team:** XGBoost + SHAP -> GNN -> Federated Learning.
    *   **War Room:** The Next.js dashboard tracking adversarial co-evolution.

**Slide 5: USP 1 - Autonomous Red Teaming (Zero-Day Discovery)**
*   Instead of waiting for fraud to happen, our RL agents *invent* fraud.
*   They probe the Blue Team's boundaries using Transaction Fuzzing.

**Slide 6: USP 2 - Explainable AI (SHAP Waterfall)**
*   Mastercard needs trust. Black-box models are unacceptable for compliance.
*   VANGUARD uses TreeExplainer (SHAP) to explain *exactly* why a transaction was blocked in real-time. (e.g., "Amount Z-Score + Mule Chain Depth").

**Slide 7: USP 3 - Federated Mule Detection**
*   Fraudsters use cross-bank mule networks. Bank A can't see Bank B's data.
*   VANGUARD implements Federated Learning: training a global model on local patterns without sharing PII, boosting detection of complex mule chains by 12.8%.

**Slide 8: USP 4 - Protection for Agentic Commerce (AP4M)**
*   As AI agents (AP4M) start buying things for humans, how do we know if the agent went rogue or was prompted-injected?
*   VANGUARD introduces "Know Your Agent" (KYA) monitoring.

**Slide 9: The Tech Stack**
*   **Simulation:** Python, NetworkX, Stable-Baselines3 (RL).
*   **Models:** XGBoost, Scikit-Learn, SHAP.
*   **Backend:** FastAPI, WebSockets (real-time).
*   **Frontend:** Next.js 14, Tailwind, Recharts.

**Slide 10: Future Roadmap**
*   Integration with Mastercard Decision Intelligence Pro.
*   Quantum-resistant encryption for federated payloads.
*   Real-time voice biometric analysis for Vishing detection.

---

## 2. Research & Documentation Tasks

### Data Dictionary Definition

You must document the exact features the Blue Team is using. This proves to the judges you understand ML feature engineering.

**Behavioral Features:**
*   `txn_count_last_1h`: High velocity indicates bot activity.
*   `unique_receivers_last_24h`: Spikes indicate bust-out or mule dispersal.
*   `amount_zscore`: Statistical deviation from the user's historical norm.
*   `time_since_last_txn_seconds`: Micro-second intervals indicate programmatic API exploitation.

**Graph Features (Mule Networks):**
*   `mule_chain_depth`: Number of hops a transaction takes between accounts within 10 minutes.

### The 12 Attack Vectors (Deep Dive)

Document these for the team so Member A knows exactly what to simulate:

1.  **Synthetic ID Bust-Out:** Build trust for 6 months, then max out credit across 50 simulated accounts simultaneously.
2.  **Deepfake Voice/Video ATO:** Bypass biometric checks (simulated as high-confidence login but anomalous device IP).
3.  **Adversarial Document Injection:** Poisoning KYC data.
4.  **Adversarial Txn Fuzzing:** RL agent alters amounts slightly (e.g., ₹49,999 instead of ₹50,000) to find the exact threshold of the Blue Team model.
5.  **API Exploit & Replay:** Replaying a valid transaction token multiple times.
6.  **Merchant Collusion:** "Ghost" transactions between a synthetic user and a fraudulent merchant terminal.
7.  **Hyper-Personalized Vishing:** Scammer knows exact recent transactions (simulated as large transfer to new receiver after a long phone call).
8.  **AI Pig Butchering:** Slow drain of funds to international wires after a specific communication pattern.
9.  **Digital Arrest Scam:** Panic-induced immediate RTGS transfer to a "government" account.
10. **Agentic Commerce Hijack:** Prompt-injecting a user's shopping bot to buy gift cards.
11. **Model Poisoning:** Slowly feeding normal-looking fraud into the training data to degrade Blue Team accuracy.
12. **Supply Chain BEC:** Invoice fraud using compromised vendor emails.

---

## 3. Creating the Final Deliverables

1.  **Pitch Deck:** Use Canva, Google Slides, or PowerPoint based on the outline above. Export as `Project_AEGIS_Pitch.pdf`.
2.  **Architecture Diagram:** Use draw.io or Excalidraw. Include the closed-loop Red/Blue cycle.
3.  **Walkthrough Video Script:**
    *   *0:00-0:30:* The Problem (GenAI Fraud).
    *   *0:30-1:00:* Launching the War Room Dashboard.
    *   *1:00-1:30:* Triggering a Red Team attack (e.g., Fuzzing).
    *   *1:30-2:30:* Showing the Blue Team catching it, the SHAP explanation, and the Federated Learning boost.
    *   *2:30-3:00:* Conclusion and Mastercard Integration potential.

**End of Member C Guide.**

## 4. Implementation Steps (Run These)

### File 1: `docs/member_c_scripts/generate_pitch.py`
Run this script to auto-generate the base PowerPoint presentation for Project VANGUARD.

```bash
cd /Users/swarup/Mastercard_Innovation_Challenge_2026/vanguard
source .venv/bin/activate
python docs/member_c_scripts/generate_pitch.py
```

### File 2: `docs/member_c_scripts/extract_data_dictionary.py`
Run this script to automatically pull the features from the transaction schema and output a clean Markdown Data Dictionary.

```bash
cd /Users/swarup/Mastercard_Innovation_Challenge_2026/vanguard
source .venv/bin/activate
python docs/member_c_scripts/extract_data_dictionary.py
```
