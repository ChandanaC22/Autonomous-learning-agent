import sys
from unittest.mock import patch, MagicMock

# Mock heavy components BEFORE importing agent/app to prevent downloads
with patch('langchain_huggingface.HuggingFaceEmbeddings'), \
     patch('langchain_community.vectorstores.Chroma'):
    from agent import app, Checkpoint

def test_mocked_loopback():
    print(f"\n{'='*20} TESTING MOCKED LOOP-BACK (FINAL) {'='*20}")
    
    initial_state = {
        "checkpoint": Checkpoint(topic="Mock Test", objectives=["Obj 1"], success_criteria=["Criteria"]),
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
        "simulated_answers": True,
        "simulated_score": 50.0 
    }
    
    nodes_visited = []
    
    # Mocking all external calls
    with patch('search_utils.gather_context_from_web', return_value="Mocked search results."), \
         patch('search_utils.search_for_simple_explanation', return_value="Mocked simple results."), \
         patch('search_utils.validate_relevance', return_value=(True, 90.0)), \
         patch('context_utils.generate_summary', return_value="Mocked summary."), \
         patch('context_utils.generate_mcqs', return_value=[MagicMock(question="Q1", options=["A","B","C","D"], correct_index=0)]), \
         patch('context_utils.generate_feynman_explanation', return_value="Mocked Feynman."), \
         patch('context_utils.chunk_text', return_value=["chunk1"]), \
         patch('context_utils.setup_vector_store', return_value=MagicMock()):
        
        print("Running mocked graph flow...")
        try:
            for output in app.stream(initial_state):
                for key, value in output.items():
                    print(f"Node [V]: {key}")
                    nodes_visited.append(key)
                    
                    if len(nodes_visited) >= 2:
                        if nodes_visited[-2] == "remedial" and nodes_visited[-1] == "questions":
                            print("✅ SUCCESS: Loop-back detected (remedial -> questions)")
                            return True
                    
                if len(nodes_visited) > 20: break
        except Exception as e:
            print(f"Error: {e}")
            
    return False

if __name__ == "__main__":
    if test_mocked_loopback():
        print("\nPASSED: Loop-back logic is verified.")
    else:
        print("\nFAILED: Loop-back logic is incorrect.")
