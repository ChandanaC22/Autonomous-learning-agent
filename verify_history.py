import requests
import time

API_URL = "http://127.0.0.1:8000"

def test_history():
    print("--- Testing Student Tracking History ---")
    
    # 1. Start learning a new topic
    print("1. Starting learning session for 'Python History Test'...")
    resp = requests.post(f"{API_URL}/start", json={
        "topic": "Python History Test",
        "objectives": ["Understand Python's origin", "Evolution of versions"]
    })
    if resp.status_code != 200:
        print(f"FAILED: /start returned {resp.status_code}")
        print(resp.text)
        return
    
    data = resp.json()
    session_id = data["session_id"]
    print(f"SUCCESS: Session ID {session_id} created.")
    
    # 2. Get the quiz
    print("2. Fetching quiz...")
    resp = requests.get(f"{API_URL}/quiz", params={"session_id": session_id})
    if resp.status_code != 200:
        print(f"FAILED: /quiz returned {resp.status_code}")
        return
    
    quiz_data = resp.json()
    questions = quiz_data["questions"]
    print(f"SUCCESS: Found {len(questions)} questions.")
    
    # 3. Submit quiz with some wrong answers
    print("3. Submitting quiz answers (partial success)...")
    # We'll just pick index 0 for all for now, assuming index 0 might be right or wrong
    user_answers = [0] * len(questions)
    resp = requests.post(f"{API_URL}/submit", params={"session_id": session_id}, json={
        "user_answers": user_answers
    })
    if resp.status_code != 200:
        print(f"FAILED: /submit returned {resp.status_code}")
        print(resp.text)
        return
    
    submit_data = resp.json()
    print(f"SUCCESS: Score: {submit_data['score']}%, Missed Indices: {submit_data['missed_indices']}")
    
    # 4. Check history
    print("4. Checking history...")
    resp = requests.get(f"{API_URL}/history")
    if resp.status_code != 200:
        print(f"FAILED: /history returned {resp.status_code}")
        return
    
    history = resp.json()
    found = any(s["id"] == session_id for s in history)
    if found:
        print(f"SUCCESS: Session {session_id} found in history.")
    else:
        print(f"FAILED: Session {session_id} NOT found in history.")
        return

    # 5. Check session details
    print(f"5. Checking session {session_id} details...")
    resp = requests.get(f"{API_URL}/sessions/{session_id}")
    if resp.status_code != 200:
        print(f"FAILED: /sessions/{session_id} returned {resp.status_code}")
        return
    
    details = resp.json()
    if details["missed_indices"] == submit_data["missed_indices"] and details["id"] == session_id:
        print("SUCCESS: Session details match submission.")
    else:
        print(f"FAILED: Details mismatch. Details: {details}")

if __name__ == "__main__":
    test_history()
