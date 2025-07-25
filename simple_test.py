

import requests
import json

def test_backend():
    print("Testing backend connection...")
    
    # URLs to test
    urls = [
        "http://localhost:8001/health",
        "http://localhost:8001/api/v1/invoice/debug",
    ]
    
    for url in urls:
        try:
            print(f"Testing {url}...")
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)}")
            else:
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_backend()