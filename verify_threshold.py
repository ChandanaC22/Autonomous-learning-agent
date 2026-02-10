from agent import app, Checkpoint
import os

def test_threshold(simulated_score):
    print(f"\n{'='*20} TESTING SCORE: {simulated_score}% {'='*20}")
    
    initial_checkpoint = Checkpoint(
        topic="Testing Threshold",
        objectives=["Verify branching"],
        success_criteria=["Score > 70"]
    )
    
    # We use a simplified state to speed up the test loop
    # We simulate being at the 'questions' node already or just starting with simulation flags
    state = {
        "checkpoint": initial_checkpoint,
        "gathered_info": ["Relevant context for testing."],
        "is_relevant": True,
        "iterations": 1,
        "messages": [],
        "questions": ["Q1?"],
        "mcqs": [],
        "summary": "Summary text.",
        "answers": [],
        "score": 0.0,
        "simulated_answers": True, # Flag for simulation mode
        "simulated_score": simulated_score # The score we want to test
    }
    
    # Run the graph
    # In simulation mode, 'questions' node will set the score and finish
    # Then it should go to 'verify' and then 'remedial' or END
    
    print(f"Running graph for simulated score: {simulated_score}...")
    final_state = state
    for output in app.stream(state):
        for key, value in output.items():
            print(f"Node '{key}' completed.")
            final_state.update(value)
            
            # Since our __main__ logic is in agent.py's __main__, 
            # we need to simulate the score injection if we use app.stream directly
            if key == "questions":
                final_state["score"] = simulated_score
    
    print(f"Final Path Decision: {'REMEDIAL' if final_state['score'] < 70 else 'COMPLETE'}")
    return final_state

if __name__ == "__main__":
    # Test case 1: Failing score
    print("Testing Remediation Path...")
    res1 = test_threshold(50.0)
    
    # Test case 2: Passing score
    print("\nTesting Success Path...")
    res2 = test_threshold(85.0)
    
    print("\nVerification Finished.")
