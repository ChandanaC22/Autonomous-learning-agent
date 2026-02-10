import os
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, END
from models import AgentState, Checkpoint, MCQ
from search_utils import gather_context_from_web, gather_context_from_notes, validate_relevance
from context_utils import chunk_text, setup_vector_store, generate_summary, generate_mcqs, evaluate_answer
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

load_dotenv()

def start_checkpoint(state: AgentState):
    """Initializes the checkpoint process."""
    print(f"--- Starting Checkpoint: {state['checkpoint'].topic} ---")
    return {"messages": ["Starting context gathering..."], "iterations": 0}

def gather_context_node(state: AgentState):
    """Gathers context from notes or web search."""
    checkpoint = state["checkpoint"]
    print(f"--- Gathering Context for: {checkpoint.topic} ---")
    
    # Prioritize notes
    context = gather_context_from_notes(checkpoint.topic)
    
    if not context:
        print("No notes found, falling back to web search...")
        context = gather_context_from_web(checkpoint.topic, checkpoint.objectives)
    
    # Update the checkpoint object with the context
    new_checkpoint = Checkpoint(
        topic=checkpoint.topic,
        objectives=checkpoint.objectives,
        success_criteria=checkpoint.success_criteria,
        context=context
    )
    
    return {
        "gathered_info": [context],
        "checkpoint": new_checkpoint,
        "messages": state["messages"] + ["Context gathered."]
    }

def validate_context_node(state: AgentState):
    """Validates the relevance of gathered context."""
    checkpoint = state["checkpoint"]
    print(f"--- Validating Context ---")
    
    is_relevant, score = validate_relevance(checkpoint.topic, checkpoint.objectives, checkpoint.context)
    print(f"Relevance Score: {score:.1f}%")
    
    return {
        "is_relevant": is_relevant,
        "relevance_score": score,
        "iterations": state["iterations"] + 1,
        "messages": state["messages"] + [f"Relevance check: {is_relevant} (Score: {score:.1f}%)"]
    }

def process_context_node(state: AgentState):
    """Chunks and vectors the context."""
    print("--- Processing Context (Chunking & Vectoring) ---")
    checkpoint = state["checkpoint"]
    chunks = chunk_text(checkpoint.context)
    # Note: We don't store the vector store in the state because it's not serializable.
    state["messages"].append(f"Processed into {len(chunks)} chunks.")
    return {"messages": state["messages"]}

def summarize_node(state: AgentState):
    """Generates a study summary for the user."""
    print("--- Generating Study Material ---")
    checkpoint = state["checkpoint"]
    summary = generate_summary(checkpoint.context, checkpoint.topic)
    return {
        "summary": summary,
        "messages": state["messages"] + ["Study material generated."]
    }

def generate_questions_node(state: AgentState):
    """Generates 3-5 MCQs based on the context, avoiding previous ones."""
    print("--- Generating MCQs ---")
    checkpoint = state["checkpoint"]
    seen = state.get("seen_questions", [])
    mcqs = generate_mcqs(checkpoint.context, checkpoint.topic, seen_questions=seen)
    
    # Track new questions to avoid them in future iterations
    new_seen = seen + [m.question for m in mcqs]
    
    return {
        "mcqs": mcqs,
        "seen_questions": new_seen,
        "messages": state["messages"] + [f"Generated {len(mcqs)} fresh MCQs."]
    }

def verify_understanding_node(state: AgentState):
    """
    Evaluates MCQ answers and updates the score in the state.
    Supports both interactive CLI input and simulated scores.
    Identifies knowledge gaps for remediation.
    """
    if state.get("is_streamlit", False):
        return state # Streamlit handles its own UI logic
        
    print("\n" + "="*50, flush=True)
    print("      --- ASSESSMENT TIME (Options 1-4) ---      ", flush=True)
    print("="*50, flush=True)
    
    mcqs = state.get("mcqs", [])
    missed_indices = []
    
    # Check for simulation mode first
    if state.get("simulated_answers"):
        print("\n--- SIMULATION MODE DETECTED ---", flush=True)
        score = state.get("simulated_score", 0.0)
        missed_indices = state.get("missed_indices", [])
    else:
        user_selections = []
        # Phase 1: Collect ALL Answers
        for i, mcq in enumerate(mcqs):
            print(f"\nQ{i+1}: {mcq.question}", flush=True)
            for opt_idx, opt in enumerate(mcq.options):
                print(f"  {opt_idx + 1}) {opt}", flush=True)
            
            while True:
                choice = input(f"\nYour answer for Q{i+1} (1-4): ").strip()
                if choice in ["1", "2", "3", "4"]:
                    break
                print("Invalid input. Please enter a number between 1 and 4.", flush=True)
                
            user_selections.append(int(choice) - 1)
        
        # Phase 2: Scoring
        correct_count = 0
        for i, selection in enumerate(user_selections):
            if selection == mcqs[i].correct_index:
                correct_count += 1
            else:
                missed_indices.append(i)
        
        score = (correct_count / len(mcqs)) * 100 if mcqs else 0
        
    print(f"\n--- Assessment Result: {score:.1f}% ---", flush=True)
    return {
        "score": score, 
        "missed_indices": missed_indices,
        "messages": state["messages"] + [f"Quiz completed with score: {score:.1f}%"]
    }

def remedial_node(state: AgentState):
    """
    Executes the Feynman Technique remediation for missed concepts.
    Loops through identified knowledge gaps and provides simplified explanations.
    """
    # For Streamlit, the node itself is a passthrough for the state, 
    # but we still want the loop logic to work if we aren't in Streamlit
    if state.get("is_streamlit", False) and not state.get("simulated_answers"):
        return state 
        
    print("\n--- ENTERING REMEDIAL PATH ---", flush=True)
    print("Your score was below 70%. Let's review the missed concepts using the Feynman Technique.", flush=True)
    
    mcqs = state.get("mcqs", [])
    checkpoint = state["checkpoint"]
    missed_indices = state.get("missed_indices", [])
    
    if missed_indices:
        print("\n" + "="*50, flush=True)
        print("      --- REMEDIATION: FEYNMAN REINFORCEMENT ---      ", flush=True)
        print("="*50, flush=True)
        print(f"Relevance Score of Source Material: {state.get('relevance_score', 0):.1f}%", flush=True)
        
        for idx in missed_indices:
            mcq = mcqs[idx]
            print(f"\nReinforcing Concept: '{mcq.question}'", flush=True)
            print(f"The correct answer was: {mcq.options[mcq.correct_index]}", flush=True)
            print("-" * 30, flush=True)
            
            from search_utils import search_for_simple_explanation
            from context_utils import generate_feynman_explanation
            
            print("Consulting pedagogical resources for the best analogy...", flush=True)
            simple_context = search_for_simple_explanation(mcq.question)
            feynman_expl = generate_feynman_explanation(mcq.question, checkpoint.context, simple_context)
            
            print("\nHere is a simpler way to think about it:", flush=True)
            print(feynman_expl, flush=True)
            print("--------------------------------", flush=True)
            
            if not state.get("simulated_answers"):
                input("Press Enter to continue to the next missed concept...")
            
    print("\nRemediation complete. Returning for re-assessment...", flush=True)
    return {"messages": state["messages"] + ["Remediation (Feynman Technique) complete."]}

def decide_assessment_result(state: AgentState):
    """Conditional logic: proceed if score >= 70%, else go to remedial."""
    score = state.get("score", 0)
    if score >= 70:
        print("🎉 Congratulations! You have mastered this checkpoint.", flush=True)
        return "complete"
    else:
        print("⚠️ Score below 70%. Remediation required.", flush=True)
        return "remedial"

def decide_to_continue(state: AgentState):
    """Determines whether to re-fetch context or process."""
    if state["is_relevant"]:
        print(f"--- Context Validated (Score: {state.get('relevance_score', 0):.1f}%) ---")
        return "process"
    elif state["iterations"] >= 3:
        print("--- Max Iterations Reached ---")
        return "end"
    else:
        print("--- Context Irrelevant, Retrying... ---")
        return "retry"

# Build the graph
workflow = StateGraph(AgentState)

# ... (nodes and edges stay the same)
workflow.add_node("start", start_checkpoint)
workflow.add_node("gather", gather_context_node)
workflow.add_node("validate", validate_context_node)
workflow.add_node("process", process_context_node)
workflow.add_node("summarize", summarize_node)
workflow.add_node("questions", generate_questions_node)
workflow.add_node("verify", verify_understanding_node)
workflow.add_node("remedial", remedial_node)

workflow.set_entry_point("start")
workflow.add_edge("start", "gather")
workflow.add_edge("gather", "validate")

workflow.add_conditional_edges(
    "validate",
    decide_to_continue,
    {
        "process": "process",
        "retry": "gather",
        "end": END
    }
)

workflow.add_edge("process", "summarize")
workflow.add_edge("summarize", "questions")
workflow.add_edge("questions", "verify")

workflow.add_conditional_edges(
    "verify",
    decide_assessment_result,
    {
        "complete": END,
        "remedial": "remedial"
    }
)

workflow.add_edge("remedial", "questions")

# Setup Checkpointer
connection_string = os.getenv("DATABASE_URL")
if connection_string and "postgresql" in connection_string:
    try:
        # LangGraph PostgresSaver uses psycopg pool
        pool = ConnectionPool(conninfo=connection_string, max_size=20)
        checkpointer = PostgresSaver(pool)
        # Note: In a production app, you'd call checkpointer.setup() in a startup hook
        app = workflow.compile(checkpointer=checkpointer)
        print("✅ LangGraph using PostgreSQL checkpointer.")
    except Exception as e:
        print(f"⚠️  Failed to connect to Postgres for LangGraph: {e}. Falling back to in-memory.")
        app = workflow.compile()
else:
    print("ℹ️  LangGraph using in-memory checkpointer (no Postgres detected).")
    app = workflow.compile()

if __name__ == "__main__":
    # Define initial state
    initial_checkpoint = Checkpoint(
        topic="Python for Data Science & AI",
        objectives=["Python Basics", "Artificial Intelligence", "Machine Learning", "Deep Learning"],
        success_criteria=["Explain Python's role in AI", "Define differences between ML and DL"]
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
        "is_streamlit": False,
        "seen_questions": []
    }
    
    # Run the graph until the end or MCQ generation
    # We stop explicitly before 'verify' to handle interaction
    current_state = state
    print("--- Running Knowledge Engine ---", flush=True)
    
    for output in app.stream(current_state):
        for key, value in output.items():
            print(f"--- Node '{key}' completed ---", flush=True)
            current_state.update(value)
            
            if key == "summarize":
                print("\n" + "="*50, flush=True)
                print("      --- STUDY MATERIAL ---      ", flush=True)
                print("="*50, flush=True)
                print(value["summary"], flush=True)
                print("="*50 + "\n", flush=True)
            
            if key == "remedial":
                print("\nPress Enter to finish the remedial review...", flush=True)
                if "simulated_answers" not in current_state:
                    input()
                
    print("\n" + "="*50, flush=True)
    print("      --- LEARNING JOURNEY COMPLETE ---      ", flush=True)
    print("="*50, flush=True)
    print(f"Final Assessment Score: {current_state.get('score', 0):.1f}%", flush=True)
    print(f"Content Relevance Score: {current_state.get('relevance_score', 0):.1f}%", flush=True)
    
    if current_state.get("score", 0) >= 70:
        print("Final Status: ✅ Mastered", flush=True)
    else:
        print("Final Status: ❌ Needs Review", flush=True)
    print("="*50, flush=True)
    print("Thank you for using the Autonomous Learning Agent!", flush=True)
