# Project AEGIS

**Mastercard Innovation Challenge 2026 - AI Defense Lab for Payment Security**

Project AEGIS is an end-to-end "AI vs AI" payment security framework. It features an Adversarial War Room dashboard, a synthetic transaction generator simulating the Indian payment landscape (UPI, IMPS, RTGS), a Reinforcement Learning (RL) Red Team Agent that mutates fraud vectors to bypass defenses, and an XGBoost Baseline Blue Team model that continuously detects and adapts to zero-day attacks.

## 🚀 Quick Start Guide

This project is built using a decoupled architecture: a Next.js Frontend and a FastAPI Python Backend.

### 1. Prerequisites
- **Node.js** (v18+)
- **Python** (3.9+)
- **Docker** (optional, for containerized deployment)

### 2. Local Setup (Without Docker)

**Backend Setup:**
```bash
# 1. Navigate to the project root
cd aegis

# 2. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install xgboost shap pandas scikit-learn

# 4. Start the FastAPI backend
uvicorn backend.main:app --reload --port 8000
```
*The backend will run at http://localhost:8000*

**Frontend Setup:**
Open a new terminal window:
```bash
# 1. Navigate to the frontend directory
cd aegis/frontend

# 2. Install dependencies
npm install

# 3. Start the Next.js development server
npm run dev
```
*The frontend will run at http://localhost:3000*

### 3. Running the Adversarial Simulation (The "Data Engine")

The true power of AEGIS is the underlying Machine Learning loop. To generate transactions and watch the ML models fight:

```bash
# Ensure you are in the project root with your virtual environment activated
cd aegis
source .venv/bin/activate

# Add the current directory to your PYTHONPATH so imports resolve correctly
export PYTHONPATH=.

# Run the Adversarial Loop (Red Team vs Blue Team)
python scripts/run_adversarial_loop.py --iterations 1
```

**What this does:**
1. Generates 30,000+ realistic baseline transactions (`train_txns.csv`).
2. Trains the **Blue Team** (XGBoost Classifier) on the baseline data.
3. The **Red Team** (RL Agent) generates the next 15 days of transactions, actively mutating fraudulent parameters (like IP addresses or timings).
4. The Blue Team evaluates the Red Team's attack, logging the Bypass Rate and Accuracy, and then adapts.

All generated data is saved in `data/generated/`.

## 🧠 System Architecture

*   **`backend/`**: FastAPI server handling REST endpoints and real-time WebSocket telemetry for the dashboard.
*   **`frontend/`**: Next.js (React) application serving the Adversarial War Room dashboard. Proxies traffic to the backend to avoid CORS/port issues.
*   **`red_team/`**: Contains the `transaction_generator.py` and RL environment used to simulate sophisticated AI fraud.
*   **`blue_team/`**: Contains the defense models (`xgboost_baseline.py`) and SHAP explainability components.
*   **`scripts/`**: Utilities to quickly bootstrap the environment and run the adversarial loop.
*   **`docs/`**: Member guides, architectural plans, and the final Pitch Deck (`docs/assets/Project_AEGIS_Pitch.pptx`).

## 🐳 Docker Deployment
For easy deployment, you can spin up the entire system using Docker Compose:
```bash
docker-compose up --build
```
This will automatically build and link the frontend and backend containers.

---
*Built for the Mastercard Innovation Challenge 2026.*
