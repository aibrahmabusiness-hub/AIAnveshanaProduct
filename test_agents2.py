import requests
res = requests.post('http://localhost:8000/api/auth/login', json={'username': 'testuser', 'password': 'password'})
token = res.json().get('access_token')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
res2 = requests.get('http://localhost:8000/api/agents', headers=headers)
print("GET /api/agents:", res2.status_code)
