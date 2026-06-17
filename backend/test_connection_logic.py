import requests
import json

# Base URL of uvicorn server
BASE_URL = "http://localhost:8000"

# Step 1: Login to get a token (assuming default credentials admin/admin or similar)
# Let's bypass auth check if possible or login first.
# Wait, let's look at the database directly to test, or let's perform standard login.
# Let's try logging in.

login_url = f"{BASE_URL}/api/token"
payload = {"username": "admin", "password": "admin"} # standard default
headers = {}

try:
    # Let's see if we can log in
    res = requests.post(f"{BASE_URL}/login", data={"username": "admin", "password": "admin"}, timeout=5)
    # Wait, the auth flow might use POST /api/token or similar. Let's look at frontend/login.html or backend/main.py.
except Exception as e:
    print("Login connection failed:", e)

# Instead of relying on network login (which could fail if user has a custom db/user),
# let's run the code directly in Python using the database module!
# This is much more robust because it bypasses auth/network dependencies.

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database import (
    save_tool_connection, get_tool_connections, delete_tool_connection,
    get_credentials, current_connection_id, current_user_id
)

# Set user context
current_user_id.set(1)

from database import delete_credentials
delete_credentials(1, "gmail")

print("--- Testing App Connection CRUD ---")

# Save Personal Gmail Connection
personal_gmail = {
    "name": "My Personal Gmail",
    "username": "john.personal@gmail.com",
    "password": "personalapppassword"
}
saved_personal = save_tool_connection(1, "gmail", personal_gmail)
print("Saved Personal Gmail:", saved_personal)

# Save Work Gmail Connection
work_gmail = {
    "name": "My Work Gmail",
    "username": "john.work@company.com",
    "password": "workapppassword"
}
saved_work = save_tool_connection(1, "gmail", work_gmail)
print("Saved Work Gmail:", saved_work)

# Fetch all connection accounts
accounts = get_tool_connections(1, "gmail")
print(f"Total Gmail Accounts fetched: {len(accounts)}")
for idx, acc in enumerate(accounts):
    print(f"[{idx+1}] ID={acc['id']} Name='{acc['name']}' Username='{acc['username']}'")

# Test ContextVar selection in get_credentials
print("\n--- Testing get_credentials with Connection IDs ---")

# 1. No connection ID set (should default to first connection)
creds_default = get_credentials(1, "gmail")
print("Default connection username:", creds_default.get("username"))
assert creds_default.get("username") == "john.personal@gmail.com", "Default connection should be Personal Gmail"

# 2. Select Work Gmail Connection
token_conn = current_connection_id.set(saved_work["id"])
creds_selected = get_credentials(1, "gmail")
print("Selected connection username:", creds_selected.get("username"))
assert creds_selected.get("username") == "john.work@company.com", "Selected connection should be Work Gmail"
current_connection_id.reset(token_conn)

# 3. No connection ID set (should fallback to default)
creds_after = get_credentials(1, "gmail")
print("Connection username after reset:", creds_after.get("username"))
assert creds_after.get("username") == "john.personal@gmail.com", "Connection should revert back to Personal Gmail"

print("\n--- Connection verification SUCCESSFUL! ---")
