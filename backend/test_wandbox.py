import requests
import json

def test_wandbox():
    url = "https://wandbox.org/api/compile.json"
    payload = {
        "compiler": "gcc-head",
        "code": "#include <stdio.h>\nint main(){printf(\"hello\");return 0;}",
        "save": False
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_wandbox()
