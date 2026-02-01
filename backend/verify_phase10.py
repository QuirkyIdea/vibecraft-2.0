import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def run_test():
    print("1. Checking Health...")
    r = requests.get("http://127.0.0.1:8000/health")
    print(f"Health: {r.status_code}")
    data = r.json()
    if data.get("phase") != 10:
        print(f"FAILED: Phase is {data.get('phase')}, expected 10")
        return
    print("Phase 10 Confirmed.")

    print("\n2. Creating Project...")
    payload = {
        "title": "Phase 10 Audit Test",
        "description": "Testing immutable logs",
        "type": "RESEARCH_PAPER"
    }
    r = requests.post(f"{BASE_URL}/projects", json=payload)
    if r.status_code != 201:
        print(f"FAILED: Create project {r.status_code} {r.text}")
        return
    
    project_id = r.json()['id']
    print(f"Project Created: ID {project_id}")
    
    print("\n3. Checking Audit Logs...")
    r = requests.get(f"{BASE_URL}/projects/{project_id}/audit")
    if r.status_code != 200:
        print(f"FAILED: Get audit {r.status_code} {r.text}")
        try:
             # Try to print JSON if exists
             print(r.json())
        except:
             pass
        return
    
    logs = r.json().get("logs", [])
    print(f"Logs Found: {len(logs)}")
    
    found_creation = False
    for log in logs:
        print(f" - {log['action_type']} at {log['created_at']}")
        if log['action_type'] == "PROJECT_CREATED":
            found_creation = True
            
    if found_creation:
        print("SUCCESS: Audit log confirmed.")
    else:
        print("FAILED: PROJECT_CREATED log missing.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Error: {e}")
