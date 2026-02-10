# Energy Decision Layer (EDL)

EDL is a B2B decision intelligence system that sits above physical energy infrastructure. It provides simulations and ranked recommendations for energy operators without direct hardware control.

## Project Structure
- `backend/`: FastAPI service for logic, simulation, and decisions.
- `frontend/`: Vite-based visual dashboard (Vanilla TS + CSS).

## Running the Application

### Backend
1. Navigate to `backend/`.
2. Install requirements: `pip install -r requirements.txt`.
3. Run the server: `python -m uvicorn main:app --reload`.

### Frontend
1. Navigate to `frontend/`.
2. Install dependencies: `npm install`.
3. Run development server: `npm run dev`.

## Core Logic
The system uses a custom `DecisionEngine` and `EDLSimulator` to evaluate scenarios based on:
- Cost
- Reliability
- Risk
- Carbon Impact
