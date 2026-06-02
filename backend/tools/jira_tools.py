import json
import requests
from database import get_credentials, current_user_id

def make_jira_request(method: str, api_path: str, payload: dict = None) -> dict:
    """
    Executes a request to the Jira Cloud API using Basic Auth (Email + API Token).
    """
    user_id = current_user_id.get()
    if not user_id:
        raise ValueError("User context not established.")
        
    creds = get_credentials(user_id, "jira")
    if not creds:
        raise ValueError("Jira credentials not found. Configure them in Settings.")
        
    jira_url = creds.get("instance_url", "").rstrip("/")
    if not jira_url:
        raise ValueError("Jira Instance URL is missing.")

    email = creds.get("username")
    api_token = creds.get("password")  # The API Token is saved as password

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    url = f"{jira_url}{api_path}"
    auth = (email, api_token)

    if method.upper() == "GET":
        res = requests.get(url, headers=headers, auth=auth, timeout=15)
    elif method.upper() == "POST":
        res = requests.post(url, headers=headers, auth=auth, json=payload, timeout=15)
    else:
        raise ValueError(f"Unsupported method: {method}")
        
    if res.status_code not in [200, 201, 204]:
        raise Exception(f"Jira API error ({res.status_code}): {res.text}")
        
    if res.status_code == 204:
        return {}
        
    return res.json()

def create_issue(project_key: str, summary: str, description: str, issue_type: str = "Task") -> str:
    """
    Creates a new issue / ticket in Jira.
    """
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": issue_type
            }
        }
    }
    try:
        res = make_jira_request("POST", "/rest/api/3/issue", payload)
        return json.dumps({
            "status": "success",
            "key": res.get("key"),
            "id": res.get("id"),
            "message": "Jira issue created successfully."
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def get_issues(project_key: str, limit: int = 5) -> str:
    """
    Retrieves recent issues from a Jira project.
    """
    try:
        res = make_jira_request("GET", f"/rest/api/3/search?jql=project={project_key}&maxResults={limit}")
        issues = res.get("issues", [])
        formatted = []
        for issue in issues:
            fields = issue.get("fields", {})
            formatted.append({
                "key": issue.get("key"),
                "id": issue.get("id"),
                "summary": fields.get("summary"),
                "status": fields.get("status", {}).get("name"),
                "issue_type": fields.get("issuetype", {}).get("name")
            })
        return json.dumps({"status": "success", "issues": formatted})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def add_comment(issue_key: str, comment: str) -> str:
    """
    Adds a comment to an existing Jira issue.
    """
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment
                        }
                    ]
                }
            ]
        }
    }
    try:
        res = make_jira_request("POST", f"/rest/api/3/issue/{issue_key}/comment", payload)
        return json.dumps({
            "status": "success",
            "id": res.get("id"),
            "message": "Comment added successfully."
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
