# ATLASGlobal: The Sentient Grid Operating System

**ATLASGlobal** is an enterprise-grade AI operating system built to orchestrate and defend critical energy infrastructure. We are evolving the power grid from a reactive "Smart Grid" into a proactive, mathematically verified **"Sentient Grid."** 

The global energy sector is facing a crisis driven by four converging forces: volatile renewable generation, aging infrastructure vulnerabilities, decarbonization imperatives, and rapid geopolitical supply shocks. ATLASGlobal solves this by replacing fragile, static grid policies with a dynamic, 4-stage Artificial Intelligence pipeline.

## The Architecture of Sentience

ATLASGlobal operates continuously within a **Hybrid Digital Twin** environment, fusing physical grid telemetry (IEC 61850 / DNP3) with advanced AI paradigms verified for harsh, mission-critical deployment:

1. **The Shield (Adversarial Robustness & PINNs)**: Before processing data, Physics-Informed Neural Networks ensure incoming SCADA signals adhere to Kirchhoff's laws and thermal physics, mathematically quarantining structural anomalies and cyber-spoofed data.
2. **The Oracle (Probabilistic Forecasting)**: Transitioning beyond deterministic guesses, we utilize Continuous Bayesian Probabilistic Models to forecast volatile demand (EVs) and renewable generation, producing strict confidence intervals.
3. **The Engine Room (Reinforcement Learning)**: Deep dispatch optimization replacing traditional Linear Programming. The AI simulates thousands of counterfactual scenarios instantly, balancing cost, carbon, and hardware degradation.
4. **The Judge (Governance & Deep XAI)**: A continuous Multivariate Regression and Variance Decomposition layer. We don't just supply an answer; we generate cryptographic statistical proofs explaining exactly *why* an autonomous decision is safe for the grid.

## Project Structure
- `backend/`: FastAPI service powering the Decision Engine, SCADA ingestion, physical grid physics models, and XAI Governance.
- `frontend/`: Vite-based 3D Mission Control. A glassmorphism command center providing unified 1D (Schematic), 2D (GIS), and 3D (Substation) spatial intelligence.

## Running the Mission Control

### Backend Engine
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend Digital Twin
```bash
cd frontend
npm install
npm run dev
```

*Built to ensure global energy sovereignty and grid resilience.*
