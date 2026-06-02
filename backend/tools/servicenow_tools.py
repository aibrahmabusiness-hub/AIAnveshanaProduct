import json
import requests
from database import get_credentials, current_user_id

def make_servicenow_request(method: str, api_path: str, payload: dict = None) -> dict:
    """
    Executes a request to the ServiceNow API, loading user credentials.
    Supports OAuth Resource Owner flow and falls back to Basic Auth.
    """
    user_id = current_user_id.get()
    if not user_id:
        raise ValueError("User context not established. Please make sure you are logged in.")
        
    creds = get_credentials(user_id, "servicenow")
    if not creds:
        raise ValueError("ServiceNow credentials not found. Configure them in Settings.")
        
    instance_url = creds.get("instance_url", "").rstrip("/")
    if not instance_url:
        raise ValueError("ServiceNow Instance URL is missing.")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    auth = None
    
    # Check if OAuth is configured
    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")
    username = creds.get("username")
    password = creds.get("password")
    
    if client_id and client_secret:
        try:
            token_url = f"{instance_url}/oauth_token.do"
            token_payload = {
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": password
            }
            token_res = requests.post(token_url, data=token_payload, timeout=10)
            if token_res.status_code == 200:
                token = token_res.json().get("access_token")
                headers["Authorization"] = f"Bearer {token}"
            else:
                auth = (username, password)
        except Exception:
            auth = (username, password)
    else:
        auth = (username, password)

    url = f"{instance_url}{api_path}"
    
    if method.upper() == "GET":
        res = requests.get(url, headers=headers, auth=auth, timeout=15)
    elif method.upper() == "POST":
        res = requests.post(url, headers=headers, auth=auth, json=payload, timeout=15)
    elif method.upper() == "PUT":
        res = requests.put(url, headers=headers, auth=auth, json=payload, timeout=15)
    else:
        raise ValueError(f"Unsupported method: {method}")
        
    if res.status_code not in [200, 201]:
        raise Exception(f"ServiceNow API error ({res.status_code}): {res.text}")
        
    return res.json()

def create_incident(short_description: str, description: str, urgency: str = "3", severity: str = "3") -> str:
    """
    Creates a new incident record in ServiceNow.
    """
    payload = {
        "short_description": short_description,
        "description": description,
        "urgency": urgency,
        "severity": severity,
        "state": "1" # New
    }
    try:
        res = make_servicenow_request("POST", "/api/now/table/incident", payload)
        result = res.get("result", {})
        return json.dumps({
            "status": "success",
            "number": result.get("number"),
            "sys_id": result.get("sys_id"),
            "message": "Incident created successfully."
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def get_incidents(limit: int = 5, state: str = None) -> str:
    """
    Gets the latest incidents from ServiceNow.
    """
    api_path = f"/api/now/table/incident?sysparm_limit={limit}&sysparm_query=ORDERBYdescsys_created_on"
    if state:
        api_path += f"^state={state}"
    try:
        res = make_servicenow_request("GET", api_path)
        incidents = res.get("result", [])
        formatted = []
        for inc in incidents:
            formatted.append({
                "number": inc.get("number"),
                "sys_id": inc.get("sys_id"),
                "short_description": inc.get("short_description"),
                "state": inc.get("state"),
                "urgency": inc.get("urgency"),
                "created_on": inc.get("sys_created_on")
            })
        return json.dumps({"status": "success", "incidents": formatted})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def update_incident(sys_id: str, state: str, comments: str = None) -> str:
    """
    Updates the state or adds comments to a ServiceNow incident.
    """
    payload = {"state": state}
    if comments:
        payload["comments"] = comments
    try:
        res = make_servicenow_request("PUT", f"/api/now/table/incident/{sys_id}", payload)
        result = res.get("result", {})
        return json.dumps({
            "status": "success",
            "number": result.get("number"),
            "sys_id": sys_id,
            "state": result.get("state"),
            "message": "Incident updated successfully."
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def query_table(table_name: str, query: str = None, limit: int = 5) -> str:
    """
    Performs a generic search query on any ServiceNow table.
    """
    api_path = f"/api/now/table/{table_name}?sysparm_limit={limit}"
    if query:
        api_path += f"&sysparm_query={query}"
    try:
        res = make_servicenow_request("GET", api_path)
        records = res.get("result", [])
        return json.dumps({"status": "success", "table": table_name, "records": records})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
