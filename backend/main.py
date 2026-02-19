import sys
import os
import datetime
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to sys.path to import agent and models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing logic
# We need to make sure we can import these. 
# Since we are running from the backend folder, or root, let's assume we run from root for simplicity in imports,
# but for structure we put this in backend/main.py.
# If we run `uvicorn backend.main:app`, the cwd is root.
# So `import agent` works if we are in root.

try:
    from agent import app as agent_app, start_checkpoint, gather_context_node, validate_context_node, process_context_node, summarize_node, generate_questions_node, verify_understanding_node, remedial_node
    from models import AgentState, Checkpoint, MCQ
    from search_utils import search_for_simple_explanation
    from context_utils import generate_feynman_explanation
    from backend.database import init_db, get_db, MasterySession, Question, User
    from sqlalchemy.orm import Session
    from fastapi import Depends, Security
    from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
    from backend.auth_utils import create_access_token, get_password_hash, verify_password, decode_access_token
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print(f"Current sys.path: {sys.path}")
    # Fallback for development if paths are tricky
    pass

app = FastAPI(title="Autonomous Learning Agent API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. In prod, lock this down.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
class InitRequest(BaseModel):
    topic: str
    objectives: List[str]

class AnswerRequest(BaseModel):
    user_answers: List[int] # Indices of selected options

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

# --- Authentication ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --- In-Memory State Management (REPLACED BY POSTGRES) ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Autonomous Learning Agent API is running"}

@app.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    hashed_p = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_p
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/start")
def start_learning(req: InitRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    initial_checkpoint = Checkpoint(
        topic=req.topic,
        objectives=req.objectives,
        success_criteria=[f"Complete assessment for {req.topic}"]
    )
    
    state = {
        "checkpoint": initial_checkpoint,
        "gathered_info": [],
        "is_relevant": False,
        "relevance_score": 0.0,
        "iterations": 0,
        "messages": [],
        "questions": [],
        "mcqs": [],
        "summary": "",
        "answers": [],
        "score": 0.0,
        "missed_indices": [],
        "is_streamlit": True,
        "seen_questions": []
    }
    
    # Run agent nodes
    state.update(start_checkpoint(state))
    state.update(gather_context_node(state))
    state.update(validate_context_node(state))
    
    if not state["is_relevant"]:
        raise HTTPException(status_code=400, detail="Topic not relevant or context not found")
        
    state.update(process_context_node(state))
    state.update(summarize_node(state))
    
    # Persist to Database
    db_session = MasterySession(
        topic=req.topic,
        objectives=req.objectives,
        context=state["checkpoint"].context,
        summary=state["summary"],
        relevance_score=state["relevance_score"],
        user_id=current_user.id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return {
        "message": "Learning started",
        "session_id": db_session.id,
        "summary": state["summary"],
        "relevance_score": state["relevance_score"]
    }

@app.get("/quiz")
def get_quiz(session_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if session_id:
        db_session = db.query(MasterySession).filter(MasterySession.id == session_id, MasterySession.user_id == current_user.id).first()
    else:
        db_session = db.query(MasterySession).filter(MasterySession.user_id == current_user.id).order_by(MasterySession.created_at.desc()).first()
        
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # If MCQs already generated, return them
    if not db_session.mcqs:
        # Reconstruct state to run agent node
        state = {
            "checkpoint": Checkpoint(
                topic=db_session.topic,
                objectives=db_session.objectives,
                context=db_session.context,
                success_criteria=[]
            ),
            "mcqs": [],
            "seen_questions": [],
            "messages": []
        }
        state.update(generate_questions_node(state))
        
        # Save MCQs to DB
        for mcq in state["mcqs"]:
            db_question = Question(
                session_id=db_session.id,
                question=mcq.question,
                options=mcq.options,
                correct_index=mcq.correct_index
            )
            db.add(db_question)
        db.commit()
        db.refresh(db_session)
        
    return {
        "session_id": db_session.id,
        "questions": [{"id": q.id, "question": q.question, "options": q.options} for q in db_session.mcqs]
    }

@app.post("/submit")
def submit_quiz(req: AnswerRequest, session_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if session_id:
        db_session = db.query(MasterySession).filter(MasterySession.id == session_id, MasterySession.user_id == current_user.id).first()
    else:
        db_session = db.query(MasterySession).filter(MasterySession.user_id == current_user.id).order_by(MasterySession.created_at.desc()).first()
        
    if not db_session or not db_session.mcqs:
        raise HTTPException(status_code=400, detail="Session or quiz not available")
    
    mcqs = db_session.mcqs
    if len(req.user_answers) != len(mcqs):
         raise HTTPException(status_code=400, detail="Answer count mismatch")

    correct_count = 0
    missed_indices = []
    
    for i, choice_idx in enumerate(req.user_answers):
        if choice_idx == mcqs[i].correct_index:
            correct_count += 1
        else:
            missed_indices.append(i) # This will be the index in the mcqs list
            
    score_pct = (correct_count / len(mcqs)) * 100
    db_session.score = score_pct
    db_session.missed_indices = missed_indices
    db.commit()
    
    return {
        "session_id": db_session.id,
        "score": score_pct,
        "passed": score_pct >= 70,
        "missed_indices": missed_indices
    }

@app.get("/remediation")
def get_remediation(session_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if session_id:
        db_session = db.query(MasterySession).filter(MasterySession.id == session_id, MasterySession.user_id == current_user.id).first()
    else:
        db_session = db.query(MasterySession).filter(MasterySession.user_id == current_user.id).order_by(MasterySession.created_at.desc()).first()
        
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # In a real app, we might store missed_indices, 
    # but for now we can infer them or just return all if score < 70
    # Actually, the original API returned them based on global_state.
    # Let's just return all for simplicity or recalculate (the submit endpoint should ideally store them)
    
    # Recalculate missed indices if we don't store them 
    # (To be precise, the front-end might want to know WHICH ones were missed)
    # The submit endpoint returns missed_indices, maybe the frontend keeps track.
    
    explanations = []
    for q in db_session.mcqs:
        # For simplicity in this demo, treat all as candidates or filtered by caller
        simple_context = search_for_simple_explanation(q.question)
        explanation = generate_feynman_explanation(q.question, db_session.context, simple_context)
        explanations.append({
            "question": q.question,
            "explanation": explanation,
            "correct_answer": q.options[q.correct_index]
        })
        
    return {"session_id": db_session.id, "remediation": explanations}

@app.post("/reset")
def reset_state(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Delete sessions for the current user
    sessions = db.query(MasterySession).filter(MasterySession.user_id == current_user.id).all()
    for session in sessions:
        db.query(Question).filter(Question.session_id == session.id).delete()
    db.query(MasterySession).filter(MasterySession.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Database state cleared for user"}
    db.commit()
    return {"message": "All database state cleared"}
    
@app.get("/history")
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = db.query(MasterySession).filter(MasterySession.user_id == current_user.id).order_by(MasterySession.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "topic": s.topic,
            "score": s.score,
            "relevance_score": s.relevance_score,
            "created_at": s.created_at.replace(tzinfo=datetime.timezone.utc) if s.created_at.tzinfo is None else s.created_at
        } for s in sessions
    ]

@app.get("/sessions/{session_id}")
def get_session_details(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_session = db.query(MasterySession).filter(MasterySession.id == session_id, MasterySession.user_id == current_user.id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {
        "id": db_session.id,
        "topic": db_session.topic,
        "objectives": db_session.objectives,
        "summary": db_session.summary,
        "score": db_session.score,
        "relevance_score": db_session.relevance_score,
        "created_at": db_session.created_at.replace(tzinfo=datetime.timezone.utc) if db_session.created_at.tzinfo is None else db_session.created_at,
        "mcqs": [{"question": q.question, "options": q.options, "correct_index": q.correct_index} for q in db_session.mcqs],
        "missed_indices": db_session.missed_indices
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
