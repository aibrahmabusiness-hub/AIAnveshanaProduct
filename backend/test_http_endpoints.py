import sys
import os
import requests
import json

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database import create_user, get_user_by_username, current_user_id
from auth import hash_password

import random
test_username = f"testuser_{random.randint(1000, 9999)}"
pwd_hash = hash_password("testpass")
current_user_id.set(1)
user = create_user(test_username, f"{test_username}@example.com", pwd_hash)
print("Created testuser in database:", user)


BASE_URL = "http://localhost:8000"

print("\n--- Step 1: Login ---")
login_res = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": test_username, "password": "testpass"},
    headers={"Content-Type": "application/json"}
)
print("Login Status:", login_res.status_code)
if login_res.status_code != 200:
    print("Login failed, aborting HTTP tests. Output:", login_res.text)
    exit(1)

token = login_res.json().get("access_token")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("\n--- Step 2: Delete existing accounts to start fresh ---")
# Check get list first
list_res = requests.get(f"{BASE_URL}/api/credentials/gmail/accounts", headers=headers)
print("Get List Status:", list_res.status_code)
if list_res.status_code == 200:
    connections = list_res.json().get("connections", [])
    for conn in connections:
        del_res = requests.delete(f"{BASE_URL}/api/credentials/gmail/accounts/{conn['id']}", headers=headers)
        print(f"Deleted account {conn['id']} status: {del_res.status_code}")

print("\n--- Step 3: Save Connection Accounts ---")
save_payload = {
    "name": "My SMTP Work Account",
    "credentials": {
        "username": "ai.brahmabusiness@gmail.com",
        "password": "some_app_password"
    }
}
save_res = requests.post(f"{BASE_URL}/api/credentials/gmail/accounts", json=save_payload, headers=headers)
print("Save Account Status (expected 400 for invalid creds):", save_res.status_code)
assert save_res.status_code == 400, "Should fail save with 400 Bad Request due to invalid credentials"
print("Save Account Response:", save_res.json())

print("\n--- Step 4: Test Connection Endpoint ---")
test_payload = {
    "tool_name": "gmail",
    "credentials": {
        "username": "ai.brahmabusiness@gmail.com",
        "password": "some_app_password"
    }
}
test_res = requests.post(f"{BASE_URL}/api/credentials/test", json=test_payload, headers=headers)
print("Test Connection Status:", test_res.status_code)
assert test_res.status_code == 200
test_data = test_res.json()
print("Test Output:", json.dumps(test_data, indent=2))
assert test_data["status"] == "error", "Should return error status for invalid credentials"
assert "Username and Password not accepted" in test_data["message"]

print("\n--- HTTP Endpoints Verification Successful! ---")
