import urllib.request
try:
    req = urllib.request.Request("http://localhost:8000/api/tools", headers={"Authorization": "Bearer dummy"})
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
