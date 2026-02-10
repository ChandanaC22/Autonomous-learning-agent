                                                                                # Autonomous Learning Agent

## Overview
This application has been converted from a monolithic Streamlit app to a modern web architecture:
- **Backend**: FastAPI (Python)
- **Frontend**: React (Vite)

## Prerequisites
- Python 3.8+
- Node.js & npm

## How to Run

You need to run the backend and frontend in separate terminals.

### 1. Start the Backend API
From the root directory of this folder:

```bash
# If you haven't installed dependencies recently:
pip install -r requirements.txt
pip install fastapi uvicorn

# Start the server
uvicorn backend.main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

### 2. Start the Frontend UI
Open a **new terminal** window, navigate to the `frontend` folder, and start the dev server:

```bash
cd frontend

# If first time running:
npm install

# Start the UI
npm run dev
```
The application will open in your browser, typically at `http://localhost:5173`.

## Project Structure
- `backend/`: Contains the FastAPI application and API logic.
- `frontend/`: Contains the React application.
- `agent.py`, `models.py`, `*utils.py`: Core logic files shared/used by the backend.
