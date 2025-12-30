import requests
import json

# Replace with 'http://127.0.0.1:5000/generate' for local testing
API_URL = "https://offer-letter-api.onrender.com/generate"

test_payload = {
    "company_info": {
        "name": "Gemini Systems Ltd"
    },
    "candidate_info": {
        "name": "Aryan Sharma"
    },
    "role_info": {
        "title": "Senior Backend Engineer",
        "location": "Bangalore"
    },
    "compensation_info": {
        "total_ctc": 2800000  # Will show as 28.0 Lakhs
    },
    "template_text": "Standard engineering template",
    "joining_date": "2026-01-15",
    "compliance_result": {
        "benefits": ["Medical Insurance", "Performance Bonus", "Remote Setup Allowance"]
    }
}

def test_generation():
    print(f"Sending request to {API_URL}...")
    try:
        response = requests.post(API_URL, json=test_payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Download URL: {result['download_url']}")
            print(f"Preview: {result['preview']}")
        else:
            print(f"❌ Failed! Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"⚠️ Connection Error: {e}")

if __name__ == "__main__":
    test_generation()
