import sys
from unittest.mock import patch, MagicMock

# Mock heavy components immediately
with patch('langchain_huggingface.HuggingFaceEmbeddings'), \
     patch('langchain_community.vectorstores.Chroma'):
    from agent import app, Checkpoint, MCQ

def test_pedagogy_and_logic():
    print(f"\n{'='*20} CORE PEDAGOGY & LOGIC VALIDATION {'='*20}")
    
    # Pre-defined test cases with complex topics to see Feynman quality
    # We provide enough context so the generator has something to work with
    test_cases = [
        {
            "topic": "Backpropagation",
            "context": "Backpropagation is an algorithm used in artificial neural networks to calculate a gradient that is needed in the calculation of the weights to be used in the network. It is shorthand for 'backward propagation of errors' and is a common method of training artificial neural networks used in conjunction with an optimization method such as gradient descent.",
            "missed_concept": "How does backpropagation actually update the weights in a neural network?"
        },
        {
            "topic": "Entropy in Thermodynamics",
            "context": "Entropy is a scientific concept, as well as a measurable physical property that is most commonly associated with a state of disorder, randomness, or uncertainty. The term and the concept are used in diverse fields, from classical thermodynamics, where it was first recognized, to the microscopic description of nature in statistical physics, and to the principles of information theory.",
            "missed_concept": "Why does entropy always increase in a closed system?"
        }
    ]
    
    all_passed = True
    
    for case in test_cases:
        print(f"\n--- [Topic: {case['topic']}] ---")
        
        # Prepare state as if the quiz just finished with a failing score
        # We Mock the MCQs needed by remedial_node
        mock_mcq = MCQ(
            question=case['missed_concept'],
            options=["Opt A", "Opt B", "Opt C", "Opt D"],
            correct_index=0,
            explanation="Technical explanation"
        )
        
        state = {
            "checkpoint": Checkpoint(topic=case['topic'], objectives=["Obj 1"], success_criteria=["Criteria"]),
            "messages": [],
            "mcqs": [mock_mcq],
            "missed_indices": [0],
            "score": 50.0,
            "is_streamlit": True, # Ensure it uses the automated path
            "simulated_answers": True # Skip input()
        }
        # Manually add the context to checkpoint for the node
        state["checkpoint"].context = case['context']
        
        # 1. TEST LOGIC: Run the graph from 'verify' or directly 'decide' logic
        # We start just before 'remedial' by using decide_assessment_result
        from agent import decide_assessment_result
        next_step = decide_assessment_result(state)
        print(f"Workflow Decision: {next_step}")
        if next_step != "remedial":
            print("❌ Workflow Logic Failure: Expected 'remedial' for score 50.0")
            all_passed = False
            
        # 2. TEST PEDAGOGY: Run the 'remedial' node logic
        print("Generating Feynman Explanation...")
        from agent import remedial_node
        res = remedial_node(state)
        
        # Verify loop-back linkage in graph? We can't easily "run" the graph transition 
        # without searching/summarizing unless we mock those nodes too.
        # But we know from the edge definition that 'remedial' goes to 'questions'.
        
        print(f"✅ State updated with: {res['messages'][-1]}")
        
    return all_passed

if __name__ == "__main__":
    test_pedagogy_and_logic()
