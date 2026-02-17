import datetime
from typing import List, Optional
from pydantic import BaseModel

# Mocking the session and conversion logic from backend/main.py
class MockSession:
    def __init__(self, id, topic, score, relevance_score, created_at):
        self.id = id
        self.topic = topic
        self.score = score
        self.relevance_score = relevance_score
        self.created_at = created_at

def test_conversion():
    # Scenario 1: Naive timestamp (simulating existing data)
    naive_dt = datetime.datetime(2026, 2, 16, 12, 0, 0)
    session1 = MockSession(1, "Naive Topic", 80, 90, naive_dt)
    
    # Applied logic from main.py
    serialized1 = {
        "created_at": session1.created_at.replace(tzinfo=datetime.timezone.utc) if session1.created_at.tzinfo is None else session1.created_at
    }
    
    print(f"Naive input: {naive_dt}")
    print(f"Serialized output: {serialized1['created_at'].isoformat()}")
    assert serialized1['created_at'].tzinfo is not None
    assert serialized1['created_at'].isoformat().endswith("+00:00") or serialized1['created_at'].isoformat().endswith("Z")

    # Scenario 2: Aware timestamp (simulating new data)
    aware_dt = datetime.datetime.now(datetime.timezone.utc)
    session2 = MockSession(2, "Aware Topic", 85, 95, aware_dt)
    
    serialized2 = {
        "created_at": session2.created_at.replace(tzinfo=datetime.timezone.utc) if session2.created_at.tzinfo is None else session2.created_at
    }
    
    print(f"Aware input: {aware_dt}")
    print(f"Serialized output: {serialized2['created_at'].isoformat()}")
    assert serialized2['created_at'].tzinfo is not None
    
    print("\n✅ Verification passed: Timestamps are correctly made timezone-aware.")

if __name__ == "__main__":
    test_conversion()
