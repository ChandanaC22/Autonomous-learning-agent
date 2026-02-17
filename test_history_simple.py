import requests
import time

API_URL = "http://127.0.0.1:8000"

def test_basic_connection():
    print("Testing basic connection to API...")
    try:
        resp = requests.get(f"{API_URL}/", timeout=5)
        print(f"✅ API is running: {resp.json()}")
        return True
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_history_endpoint():
    print("\nTesting /history endpoint...")
    try:
        resp = requests.get(f"{API_URL}/history", timeout=5)
        if resp.status_code == 200:
            history = resp.json()
            print(f"✅ /history endpoint works. Found {len(history)} sessions.")
            for session in history[:3]:  # Show first 3
                print(f"  - {session['topic']}: {session['score']:.1f}%")
            return True
        else:
            print(f"❌ /history returned {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error calling /history: {e}")
        return False

if __name__ == "__main__":
    print("=== Quick History Feature Test ===\n")
    if test_basic_connection():
        test_history_endpoint()
    else:
        print("\n⚠️  Make sure the backend server is running:")
        print("   python backend/main.py")
