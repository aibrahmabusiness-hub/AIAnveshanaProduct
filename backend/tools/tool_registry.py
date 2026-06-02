"""
Tool Registry: Maps tool IDs to their Gemini-compatible function definitions.
When an agent is configured with specific tools, this registry dynamically
loads only the functions that agent needs.
"""

from tools.outlook_tools import schedule_meeting, get_important_emails

# Each entry: tool_id -> { "name": display name, "functions": list of callables for Gemini }
TOOL_REGISTRY = {
    "outlook_calendar": {
        "name": "Outlook Calendar",
        "description": "Schedule and manage meetings via Microsoft Outlook",
        "functions": [],  # Will be populated below
    },
    "outlook_email": {
        "name": "Outlook Email",
        "description": "Read and send emails via Microsoft Outlook",
        "functions": [],
    },
    "gmail_read": {
        "name": "Gmail (Read)",
        "description": "Read emails from Gmail inbox",
        "functions": [],
    },
    "gmail_send": {
        "name": "Gmail (Send)",
        "description": "Send emails via Gmail",
        "functions": [],
    },
    "salesforce_query": {
        "name": "Salesforce (Query)",
        "description": "Query records from Salesforce CRM",
        "functions": [],
    },
    "salesforce_create": {
        "name": "Salesforce (Create)",
        "description": "Create records in Salesforce CRM",
        "functions": [],
    },
    "servicenow_incidents": {
        "name": "ServiceNow Incidents",
        "description": "Create, retrieve, and update ServiceNow incidents",
        "functions": [],
    },
    "servicenow_tables": {
        "name": "ServiceNow Table Queries",
        "description": "Query any ServiceNow database table generically",
        "functions": [],
    },
    "jira_issues": {
        "name": "Jira Management",
        "description": "Create, query, and add comments to issues in Jira Cloud",
        "functions": [],
    },
    "google_search": {
        "name": "Google Web Search",
        "description": "Search the live web for current facts, news, and details keylessly",
        "functions": [],
    },
}


# --- Outlook Tool Functions (for Gemini function calling) ---

def tool_schedule_meeting(subject: str, attendees: str, start_time: str) -> str:
    """
    Schedule a meeting in Microsoft Outlook.
    Args:
        subject: The subject/title of the meeting.
        attendees: Semicolon-separated list of attendee email addresses.
        start_time: Start time in ISO format (e.g., '2026-06-02T14:00:00').
    """
    return schedule_meeting(subject, attendees, start_time)

def tool_read_emails() -> str:
    """
    Retrieve the most recent unread/important emails from the Outlook inbox.
    Returns a formatted list of emails with sender, subject, and received time.
    """
    return get_important_emails(10)


def tool_google_search(query: str, limit: int = 5) -> str:
    """
    Search the live web using Google/DuckDuckGo keylessly.
    Args:
        query: The search query terms.
        limit: Max search results to fetch (default 5).
    """
    try:
        from tools.google_search import google_search as gs
        return gs(query, limit)
    except Exception as e:
        return f"Search execution error: {str(e)}"


# --- Gmail Tool Functions ---

def tool_read_gmail(limit: int = 10) -> str:
    """
    Read the most recent emails from the user's Gmail inbox.
    Args:
        limit: Maximum number of emails to retrieve (default 10).
    """
    try:
        from tools.gmail_tools import read_gmail_inbox
        return read_gmail_inbox(limit)
    except Exception as e:
        return f"Gmail Error: {str(e)}. Make sure Gmail credentials are configured in Settings."

def tool_send_gmail(to: str, subject: str, body: str) -> str:
    """
    Send an email via Gmail.
    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body text.
    """
    try:
        from tools.gmail_tools import send_gmail
        return send_gmail(to, subject, body)
    except Exception as e:
        return f"Gmail Error: {str(e)}. Make sure Gmail credentials are configured in Settings."


# --- Salesforce Tool Functions ---

def tool_query_salesforce(query: str) -> str:
    """
    Run a SOQL query against Salesforce to retrieve records.
    Args:
        query: A valid SOQL query string (e.g., 'SELECT Name FROM Account LIMIT 5').
    """
    try:
        from tools.salesforce_tools import query_salesforce
        return query_salesforce(query)
    except Exception as e:
        return f"Salesforce Error: {str(e)}. Make sure Salesforce credentials are configured in Settings."

def tool_create_salesforce_record(object_type: str, data: str) -> str:
    """
    Create a new record in Salesforce.
    Args:
        object_type: The Salesforce object type (e.g., 'Account', 'Contact', 'Lead').
        data: JSON string of field values (e.g., '{"Name": "Acme Corp"}').
    """
    try:
        from tools.salesforce_tools import create_salesforce_record
        return create_salesforce_record(object_type, data)
    except Exception as e:
        return f"Salesforce Error: {str(e)}. Make sure Salesforce credentials are configured in Settings."


# --- ServiceNow Tool Functions ---

def tool_servicenow_create_incident(short_description: str, description: str, urgency: str = "3", severity: str = "3") -> str:
    """
    Create a new incident ticket in ServiceNow.
    Args:
        short_description: Summary of the issue.
        description: Full detailed description of the incident.
        urgency: Level of urgency (1=High, 2=Medium, 3=Low).
        severity: Level of severity (1=High, 2=Medium, 3=Low).
    """
    try:
        from tools.servicenow_tools import create_incident
        return create_incident(short_description, description, urgency, severity)
    except Exception as e:
        return f"ServiceNow Error: {str(e)}. Configure ServiceNow credentials in Settings."

def tool_servicenow_get_incidents(limit: int = 5, state: str = None) -> str:
    """
    Retrieve recent ServiceNow incident tickets.
    Args:
        limit: Number of incidents to return (default 5).
        state: Optional filter for incident state (e.g. '1' for New, '2' for In Progress).
    """
    try:
        from tools.servicenow_tools import get_incidents
        return get_incidents(limit, state)
    except Exception as e:
        return f"ServiceNow Error: {str(e)}. Configure ServiceNow credentials in Settings."

def tool_servicenow_update_incident(sys_id: str, state: str, comments: str = None) -> str:
    """
    Update state or add comments to a ServiceNow incident.
    Args:
        sys_id: Unique system identifier of the incident.
        state: New state value (e.g., '2' for In Progress, '7' for Closed).
        comments: Optional work notes or comment updates.
    """
    try:
        from tools.servicenow_tools import update_incident
        return update_incident(sys_id, state, comments)
    except Exception as e:
        return f"ServiceNow Error: {str(e)}. Configure ServiceNow credentials in Settings."

def tool_servicenow_query_table(table_name: str, query: str = None, limit: int = 5) -> str:
    """
    Query records from any table in ServiceNow (e.g. 'sys_user', 'cmdb_ci').
    Args:
        table_name: ServiceNow system table name (e.g. 'sys_user').
        query: Optional ServiceNow query string (e.g. 'user_name=admin').
        limit: Maximum records to return.
    """
    try:
        from tools.servicenow_tools import query_table
        return query_table(table_name, query, limit)
    except Exception as e:
        return f"ServiceNow Error: {str(e)}. Configure ServiceNow credentials in Settings."


# --- Jira Tool Functions ---

def tool_jira_create_issue(project_key: str, summary: str, description: str, issue_type: str = "Task") -> str:
    """
    Create a new issue or task in Jira Cloud.
    Args:
        project_key: The uppercase project key (e.g., 'PROJ', 'KAN').
        summary: Title/Summary of the issue.
        description: Detailed description text of the issue.
        issue_type: Type of the issue (e.g., 'Task', 'Bug', 'Story').
    """
    try:
        from tools.jira_tools import create_issue
        return create_issue(project_key, summary, description, issue_type)
    except Exception as e:
        return f"Jira Error: {str(e)}. Configure Jira credentials in Settings."

def tool_jira_get_issues(project_key: str, limit: int = 5) -> str:
    """
    Retrieve recent Jira issues from a project.
    Args:
        project_key: The uppercase project key (e.g., 'PROJ').
        limit: Max issues to return (default 5).
    """
    try:
        from tools.jira_tools import get_issues
        return get_issues(project_key, limit)
    except Exception as e:
        return f"Jira Error: {str(e)}. Configure Jira credentials in Settings."

def tool_jira_add_comment(issue_key: str, comment: str) -> str:
    """
    Add a text comment to an existing Jira issue.
    Args:
        issue_key: The issue key (e.g., 'PROJ-123').
        comment: Text body of the comment to add.
    """
    try:
        from tools.jira_tools import add_comment
        return add_comment(issue_key, comment)
    except Exception as e:
        return f"Jira Error: {str(e)}. Configure Jira credentials in Settings."


# Register functions into the registry
TOOL_REGISTRY["outlook_calendar"]["functions"] = [tool_schedule_meeting]
TOOL_REGISTRY["outlook_email"]["functions"] = [tool_read_emails]
TOOL_REGISTRY["gmail_read"]["functions"] = [tool_read_gmail]
TOOL_REGISTRY["gmail_send"]["functions"] = [tool_send_gmail]
TOOL_REGISTRY["salesforce_query"]["functions"] = [tool_query_salesforce]
TOOL_REGISTRY["salesforce_create"]["functions"] = [tool_create_salesforce_record]
TOOL_REGISTRY["servicenow_incidents"]["functions"] = [tool_servicenow_create_incident, tool_servicenow_get_incidents, tool_servicenow_update_incident]
TOOL_REGISTRY["servicenow_tables"]["functions"] = [tool_servicenow_query_table]
TOOL_REGISTRY["jira_issues"]["functions"] = [tool_jira_create_issue, tool_jira_get_issues, tool_jira_add_comment]
TOOL_REGISTRY["google_search"]["functions"] = [tool_google_search]


def get_tools_for_agent(tool_ids: list) -> list:
    """
    Given a list of tool IDs, returns the combined list of
    Gemini-compatible callable functions.
    """
    functions = []
    for tool_id in tool_ids:
        if tool_id in TOOL_REGISTRY:
            functions.extend(TOOL_REGISTRY[tool_id]["functions"])
    return functions


def get_available_tools() -> list:
    """Returns a list of all available tools with their metadata (for the UI)."""
    return [
        {"id": tool_id, "name": info["name"], "description": info["description"]}
        for tool_id, info in TOOL_REGISTRY.items()
    ]
