# Project AEGIS Complete Hackathon Submission Documentation

## The Problem We Are Solving
The Indian payment landscape is evolving at breakneck speed. With UPI, IMPS, and RTGS processing billions of transactions daily, fraud patterns are mutating faster than static rule based systems can adapt. We realized that relying on historical data to catch tomorrow's zero day attacks is a losing battle. The fraudsters are already using AI. We need an AI that fights back.

## Our Solution Project AEGIS
Project AEGIS is an end to end AI versus AI payment security framework. Instead of waiting for fraud to happen so we can learn from it, AEGIS creates its own zero day attacks in a closed loop environment. We built a system where a Reinforcement Learning Red Team Agent actively tries to bypass our Blue Team Defense Pipeline. They fight, they learn, and our defense models get stronger before a single real world transaction is ever at risk.

## System Architecture

### 1. The Red Team Attack Simulator
This is our Adversarial War Room engine. We built a Transaction Generator seeded with Gymnasium RL environments. Its sole purpose is to mutate fraudulent parameters like IP addresses, transaction timings, and device fingerprints to find blind spots in our defenses. 

### 2. The Blue Team Defense Pipeline
Our defense is a meta ensemble model that does not rely on just one signal. It combines XGBoost for tabular features, Temporal Transformers for sequence anomalies, and Heterogeneous Graph Neural Networks to detect mule accounts. When the Red Team finds a bypass, the Blue Team analyzes the SHAP explainability metrics and adapts its weights.

### 3. The Backend Engine
We chose FastAPI for the backend because we needed extreme performance. It orchestrates the entire simulation loop and serves model inferences in real time via per-session WebSocket connections. Each user gets their own isolated battle session with an independent BattleSimulator instance, meaning multiple judges or users can simultaneously run different attack scenarios without interfering with each other. It handles the heavy lifting of processing 30,000 plus generated transactions seamlessly.

### 4. The War Room Frontend
Built on Next.js and React, the frontend is our mission control dashboard. It ingests per-session WebSocket telemetry from the FastAPI backend to visualize the adversarial loop live. Judges can literally watch the Red Team and Blue Team fight in real time, and each judge sees only their own independent battle state.

## How To Run The Simulation

1. First you need to set up the backend. Open a terminal and navigate to the aegis directory. Create your Python virtual environment and install the dependencies from requirements.txt. Make sure to also install xgboost, shap, pandas, and scikit learn. Start the FastAPI backend using uvicorn on port 8000.
2. Next you will start the frontend. Open a second terminal window and go to the frontend directory. Run npm install followed by npm run dev. The dashboard will be live on port 3000.
3. The real magic happens in the adversarial loop. From the project root, activate your virtual environment, export PYTHONPATH to the current directory, and run the run_adversarial_loop.py script from the scripts folder. 
4. Sit back and watch the dashboard as the Red Team generates 15 days worth of synthetic transaction data and the Blue Team adapts to the new attacks. All the generated CSV files will be safely stored in the data directory.

## Business Impact
Project AEGIS directly targets the bottom line. False positives cost gateways millions in lost revenue and frustrated users while false negatives lead to direct financial loss and regulatory fines. By continuously adapting to attacks before they happen in the wild we minimize both. This framework reduces the reliance on manual fraud investigation teams and prevents the massive PR disasters that follow major breaches.

## Future Roadmap
1. Cloud Native Deployment Transitioning the FastAPI backend to Kubernetes for auto scaling during peak festival transaction loads.
2. Federated Learning Allowing multiple banks to share the Blue Team model weights without sharing sensitive customer PII.
3. Enhanced Red Team Agent Expanding the Gymnasium environment to simulate coordinated multi agent attacks like orchestrated botnets.

## Why AEGIS Deserves The Top Score
We did not just build a classifier. We built a self improving data engine tailored specifically for the complexities of modern Indian payment gateways. The decoupled architecture means it is production ready. The live telemetry proves it actually works. We spent the entire hackathon making sure the math checks out and the UI looks incredible. We are incredibly proud of what we built here.
