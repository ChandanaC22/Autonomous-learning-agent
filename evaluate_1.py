import os
from agent import app
from models import Checkpoint
from dotenv import load_dotenv

load_dotenv()

# Test checkpoints for evaluation
test_checkpoints = [
    {
        "topic": "Baking Sourdough Bread",
        "objectives": ["Understand the starter cultivation process", "Learn about hydration levels", "Master the stretch and fold technique"],
        "success_criteria": ["Explain what a starter is", "Calculate baker's percentages"]
    },
    {
        "topic": "React Hooks",
        "objectives": ["Understand useState and useEffect", "Learn about rules of hooks", "Implement a custom hook"],
        "success_criteria": ["Explain when to use useEffect", "Create a function called useLocalStorage"]
    },
    {
        "topic": "Photosynthesis",
        "objectives": ["Distinguish between light-dependent and light-independent reactions", "Understand the role of chlorophyll", "Explain the Calvin cycle"],
        "success_criteria": ["Draw the photosynthesis equation", "Describe where reactions occur in the chloroplast"]
    },
    {
        "topic": "Machine Learning: Linear Regression",
        "objectives": ["Understand the cost function", "Learn about gradient descent", "Implement linear regression using scikit-learn"],
        "success_criteria": ["Define 'slope' and 'intercept'", "Explain why we minimize the mean squared error"]
    },
    {
        "topic": "History of the Roman Empire",
        "objectives": ["Analyze the transition from Republic to Empire", "Understand the role of Julius Caesar", "Discuss the reasons for the fall of the Western Roman Empire"],
        "success_criteria": ["Name three Roman Emperors", "List two factors contributing to the empire's decline"]
    }
]

def run_evaluation():
    print("=== STARTING EVALUATION: CONTEXT RELEVANCE SCORE ===")
    results = []
    
    for i, cp_data in enumerate(test_checkpoints):
        print(f"\n--- Testing Checkpoint {i+1}: {cp_data['topic']} ---")
        
        checkpoint = Checkpoint(**cp_data)
        initial_state = {
            "checkpoint": checkpoint,
            "gathered_info": [],
            "is_relevant": False,
            "iterations": 0,
            "messages": []
        }
        
        final_state = None
        for output in app.stream(initial_state):
            for key, value in output.items():
                if key == "validate":
                    final_state = value
        
        # Get the gathered context from the final state's checkpoint
        # Note: In our current implementation, the last node in stream is 'validate'
        # which returns is_relevant and iterations. We need the actual checkpoint object.
        # Let's adjust this to get the state after the full run.
        
        # In LangGraph app.stream, the last yielded value for a node is that node's output.
        # We need to see if it validated.
        
        is_relevant = final_state.get("is_relevant", False) if final_state else False
        
        print(f"Validation Result: {'PASSED' if is_relevant else 'FAILED'}")
        results.append({
            "topic": cp_data['topic'],
            "passed": is_relevant
        })

    print("\n=== EVALUATION SUMMARY ===")
    passed_count = sum(1 for r in results if r['passed'])
    print(f"Pass Rate: {passed_count}/{len(results)} ({(passed_count/len(results))*100:.1f}%)")
    
    if passed_count / len(results) >= 0.8:
        print("Success Criteria Met (>= 4/5 relevance score)")
    else:
        print("Success Criteria NOT Met. Adjust search queries or validation logic.")

if __name__ == "__main__":
    run_evaluation()
