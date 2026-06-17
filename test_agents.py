import json
import requests
import sys

res = requests.post('http://localhost:8000/api/auth/login', json={'username': 'testuser', 'password': 'password'})
if res.status_code != 200:
    print("Login failed:", res.text)
    sys.exit(1)
token = res.json()['access_token']

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
res = requests.get('http://localhost:8000/api/agents', headers=headers)
print("GET /api/agents:", res.status_code)
