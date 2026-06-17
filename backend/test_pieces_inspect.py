import requests
import json

try:
    res = requests.get("http://localhost:3001/pieces")
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print("Error:", e)
