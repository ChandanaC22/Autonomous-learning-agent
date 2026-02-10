import sys
from unittest.mock import patch, MagicMock
from agent import app, Checkpoint

def evaluate_milestone():
    print(f"\n{'='*25} MILESTONE 2 EVALUATION REPORT {'='*25}")
    
    # Test Scenarios
    scenarios = [
        {"topic": "Quantum Computing", "score": 40.0},
        {"topic": "Blockchain", "score": 25.0},
        {"topic": "Neural Networks", "score": 60.0}
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n--- Testing Scenario: {scenario['topic']} (Forced Score: {scenario['score']}%) ---")
        
        initial_state = {
            "checkpoint": Checkpoint(topic=scenario['topic'], objectives=["Core Concepts"], success_criteria=["Mastery"]),
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
            "is_streamlit": True, # Non-blocking
            "simulated_answers": True,
            "simulated_score": scenario['score']
        }
        
        nodes_visited = []
        explanations = []
        
        # We only mock the gathering/validation to ensure specific topics can be "studied"
        # But we let the Feynman generator run for real (or mock it if we want to save credits, 
        # but the user wants to review SIMPLICITY, so let's run it)
        
        try:
            for output in app.stream(initial_state):
                for key, value in output.items():
                    nodes_visited.append(key)
                    if key == "remedial" and "messages" in value:
                        # In the real node, the explanation is printed but not necessarily returned in state 
                        # as a long string for every message. Let's capture the state.
                        pass
                    
                    # Track path
                    if len(nodes_visited) > 1 and nodes_visited[-2] == "remedial" and nodes_visited[-1] == "questions":
                        print(f"✅ Loop-back verified: {nodes_visited[-2]} -> {nodes_visited[-1]}")
                    
                    if len(nodes_visited) > 12: break # Safety
            
            # Since the LLM calls are real in context_utils, we'll see the output in the console.
            # To capture it for the report, we would need to mock the print or the return value.
            # For this evaluation, I will run it and manually observe/report.
            
            results.append({
                "topic": scenario['topic'],
                "path": " -> ".join(nodes_visited),
                "loop_status": "SUCCESS" if ("remedial" in nodes_visited and "questions" in nodes_visited) else "FAILED"
            })
            
        except Exception as e:
            print(f"Error in scenario {scenario['topic']}: {e}")

    print(f"\n{'='*20} FINAL SUMMARY {'='*20}")
    for res in results:
        print(f"Topic: {res['topic']} | Path: {res['path']} | Loop: {res['loop_status']}")

if __name__ == "__main__":
    # To run a real quality test, we shouldn't mock the content generation
    # But we mock embeddings to avoid local model overhead
    with patch('langchain_huggingface.HuggingFaceEmbeddings'), \
         patch('langchain_community.vectorstores.Chroma'):
        evaluate_milestone()
