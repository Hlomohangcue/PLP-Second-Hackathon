import requests
import json

def test_backend():
    url = "http://localhost:5000/api/process-notes"
    data = {
        "notes": "Python is a programming language. It is used for web development. Variables store data. Functions perform tasks."
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_backend()
    print(f"Backend test: {'PASSED' if success else 'FAILED'}")