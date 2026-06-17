"""
Tool Registry: Maps tool IDs to their Gemini-compatible function definitions.
When an agent is configured with specific tools, this registry dynamically
loads only the functions that agent needs.
"""

from tools.outlook_tools import schedule_meeting, get_important_emails
import sys
import os

# Ensure the parent directory is in path so we can import pieces
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pieces import PIECES_REGISTRY, get_piece_action

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
    "logic_loop": {
        "name": "Logic Loop",
        "description": "Iterate over an array of items.",
        "functions": [],
    },
    "logic_if": {
        "name": "Logic If",
        "description": "Branching logic.",
        "functions": [],
    },
    "ai_prompt": {
        "name": "AI Prompt",
        "description": "Send a dynamic prompt to an LLM to generate text or classify data.",
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

def tool_read_gmail(folder: str = "inbox", status_filter: str = "ALL", sender_email: str = "", days_ago: str = "", limit: int = 10) -> str:
    """
    Read the most recent emails from the user's Gmail.
    Args:
        folder: Gmail label/folder to search (default 'inbox').
        status_filter: 'ALL', 'UNSEEN', or 'SEEN'.
        sender_email: Optional sender email to filter by.
        days_ago: Optional number of days to search back.
        limit: Maximum number of emails to retrieve (default 10).
    """
    try:
        from tools.gmail_tools import read_gmail_inbox
        return read_gmail_inbox(folder, status_filter, sender_email, days_ago, limit)
    except Exception as e:
        return f"Gmail Error: {str(e)}. Make sure Gmail credentials are configured in Settings."

def tool_mark_gmail_read(message_id: str, folder: str = "inbox") -> str:
    """
    Mark an email as read in Gmail.
    Args:
        message_id: The IMAP message ID of the email.
        folder: The folder where the email is located.
    """
    try:
        from tools.gmail_tools import mark_gmail_read
        return mark_gmail_read(message_id, folder)
    except Exception as e:
        return f"Gmail Error: {str(e)}."

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
TOOL_REGISTRY["salesforce_query"]["functions"] = [tool_query_salesforce]
TOOL_REGISTRY["salesforce_create"]["functions"] = [tool_create_salesforce_record]
TOOL_REGISTRY["servicenow_incidents"]["functions"] = [tool_servicenow_create_incident, tool_servicenow_get_incidents, tool_servicenow_update_incident]
TOOL_REGISTRY["servicenow_tables"]["functions"] = [tool_servicenow_query_table]
TOOL_REGISTRY["jira_issues"]["functions"] = [tool_jira_create_issue, tool_jira_get_issues, tool_jira_add_comment]
TOOL_REGISTRY["google_search"]["functions"] = [tool_google_search]

def tool_logic_loop(array_var: str = None) -> str:
    """Pass-through logic loop execution."""
    return f"Loop configured for variable: {array_var}"

def tool_logic_if(condition: str = None) -> str:
    """Pass-through logic if execution."""
    return f"If condition evaluated: {condition}"

def tool_ai_prompt(prompt: str = "") -> str:
    """Run a dynamic prompt through the Gemini LLM for classification, extraction, or generation."""
    try:
        import os
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return "Error: GEMINI_API_KEY environment variable is not set."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Prompt Error: {str(e)}"

TOOL_REGISTRY["logic_loop"]["functions"] = [tool_logic_loop]
TOOL_REGISTRY["logic_if"]["functions"] = [tool_logic_if]
TOOL_REGISTRY["ai_prompt"]["functions"] = [tool_ai_prompt]

# --- Inject Modular Pieces into the Registry ---
for action_id, action_data in PIECES_REGISTRY.items():
    if action_id not in TOOL_REGISTRY:
        TOOL_REGISTRY[action_id] = {
            "name": action_data.get("name", action_id),
            "description": action_data.get("description", ""),
            "functions": [action_data.get("callable")]
        }

def get_tools_for_agent(tool_ids: list) -> list:
    """
    Given a list of tool IDs, returns the combined list of
    Gemini-compatible callable functions.
    """
    from database import current_connection_id
    import functools

    def with_connection(func, connection_id):
        if not connection_id:
            return func
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            token = current_connection_id.set(connection_id)
            try:
                return func(*args, **kwargs)
            finally:
                current_connection_id.reset(token)
        return wrapper

    functions = []
    for tool_str in tool_ids:
        tid = tool_str
        conn_id = None
        if ":" in tool_str:
            tid, conn_id = tool_str.split(":", 1)
            
        if tid in TOOL_REGISTRY:
            funcs = TOOL_REGISTRY[tid]["functions"]
            functions.extend([with_connection(f, conn_id) for f in funcs])
            
    return functions


def get_available_tools() -> list:
    """Returns a list of all available tools with their metadata (for the UI)."""
    return [
        {"id": tool_id, "name": info["name"], "description": info["description"]}
        for tool_id, info in TOOL_REGISTRY.items()
    ]
