                                                                                ## Deployment

The application is configured for a split deployment:
- **Frontend**: Deployed on **Vercel** as a static site.
- **Backend**: Deployed on **Render** as a Python web service.

### Deployment Steps

#### 1. Backend (Render)
1. Join [Render.com](https://render.com) and create a new **Blueprint**.
2. Connect this repository. Render will automatically use `render.yaml`.
3. Set the following environment variables in Render:
   - `GROQ_API_KEY`: Your Groq API key.
   - `SECRET_KEY`: A secure random string for JWT.
4. Once deployed, note your service URL (e.g., `https://your-app.onrender.com`).

#### 2. Frontend (Vercel)
1. Join [Vercel.com](https://vercel.com) and import this repository.
2. In the project settings, add an environment variable:
   - `VITE_API_URL`: Set this to your Render backend URL.
3. Deploy the project.

## How to Run Locally

### 1. Start the Backend API
```bash
# Install dependencies from the backend folder
pip install -r backend/requirements.txt

# Start the server using the backend entry point
uvicorn backend.server:app --reload --port 8000
```

### 2. Start the Frontend UI
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
- `backend/`: FastAPI application, logic, and dependencies.
  - `backend/requirements.txt`: Python package list.
  - `backend/server.py`: Server entry point.
- `frontend/`: React application (Vite).
  - `frontend/vercel.json`: Handles client-side routing on Vercel.
- `render.yaml`: Configuration for Render deployment (points to `backend/`).
- `agent.py`, `models.py`, `context_utils.py`: Core logic files in root.
