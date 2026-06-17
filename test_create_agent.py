import json
import requests
import sys

# Login to get token
res = requests.post('http://localhost:8000/api/auth/login', json={'username': 'admin', 'password': 'password'})
if res.status_code != 200:
    print("Login failed:", res.text)
    sys.exit(1)

token = res.json()['access_token']

# Create agent
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
payload = {
    'name': 'Test', 'description': 'Test', 'system_prompt': 'Test', 'connected_tools': []
}
res = requests.post('http://localhost:8000/api/agents', headers=headers, json=payload)
print(res.text)
