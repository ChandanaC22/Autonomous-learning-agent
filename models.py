from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field

class Checkpoint(BaseModel):
    """
    Data structure for a learning checkpoint.
    """
    topic: str = Field(..., description="The main topic of the checkpoint.")
    objectives: List[str] = Field(..., description="The specific learning objectives for this checkpoint.")
    success_criteria: List[str] = Field(..., description="Criteria to determine if the checkpoint was successful.")
    context: Optional[str] = Field(None, description="Gathered context/information for this checkpoint.")

class MCQ(BaseModel):
    """
    Multiple Choice Question structure.
    """
    question: str = Field(..., description="The question text.")
    options: List[str] = Field(..., description="List of 4 options.")
    correct_index: int = Field(..., description="Index of the correct option (0-3).")

class AgentState(TypedDict):
    """
    The state of the LangGraph agent.
    """
    checkpoint: Checkpoint
    gathered_info: List[str]
    is_relevant: bool
    relevance_score: float
    iterations: int
    messages: List[str]
    questions: Optional[List[str]]
    mcqs: Optional[List[MCQ]]
    summary: Optional[str]
    answers: Optional[List[str]]
    score: Optional[float]
    missed_indices: Optional[List[int]]
    feynman_explanation: Optional[str]
    feynman_feedback: Optional[str]
    seen_questions: Optional[List[str]]
