import requests

base_url = "http://localhost:8000"
res = requests.post(f"{base_url}/api/auth/login", json={"username": "admin", "password": "password"})
token = res.json().get("access_token")

res2 = requests.get(f"{base_url}/api/workflows", headers={"Authorization": f"Bearer {token}"})
data = res2.json()
if "workflows" in data:
    for w in data["workflows"]:
        print("ID:", w.get("id"), "Agent:", w.get("agent_id"), "Name:", w.get("name").encode("utf-8"))
else:
    print(data)
