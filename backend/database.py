import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from dotenv import load_dotenv

load_dotenv()

# Fallback to local SQLite if Postgres is not available or specified
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or "postgresql" not in DATABASE_URL:
    print("⚠️  PostgreSQL URL not found or invalid. Falling back to local SQLite (autolearner.db).")
    DATABASE_URL = "sqlite:///./autolearner.db"
    # SQLite needs special argument for multi-threading in some cases
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(DATABASE_URL)
        # Try to connect once to verify
        with engine.connect() as conn:
            pass
    except Exception as e:
        print(f"⚠️  PostgreSQL connection failed: {e}. Falling back to SQLite.")
        DATABASE_URL = "sqlite:///./autolearner.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    sessions = relationship("MasterySession", back_populates="user")

class MasterySession(Base):
    __tablename__ = "mastery_sessions"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    objectives = Column(JSON)  # List of strings
    context = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    relevance_score = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    missed_indices = Column(JSON, nullable=True)  # List of indices of missed MCQs
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="sessions")
    mcqs = relationship("Question", back_populates="session", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mastery_sessions.id"))
    question = Column(Text)
    options = Column(JSON) # List of strings
    correct_index = Column(Integer)

    session = relationship("MasterySession", back_populates="mcqs")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
