from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal
from enum import Enum
import json

# Workflow Structure


class NodeData(BaseModel):
    label: str
    piece: str
    config: Dict[str, Any] = Field(default_factory=dict)

class Node(BaseModel):
    id: str
    data: NodeData
    position: Dict[str, float]

class Edge(BaseModel):
    source: str
    target: str
    id: Optional[str] = None

class WorkflowSchema(BaseModel):
    workflow_id: Optional[str] = None
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)

# Piece Types
class PieceType(str, Enum):
    # Triggers
    TRIGGER_MANUAL = "manual"
    TRIGGER_WEBHOOK = "webhook"
    TRIGGER_SCHEDULE = "schedule"
    
    # Email
    ACTION_GMAIL = "gmail"
    ACTION_SMTP = "smtp"
    
    # Communication
    ACTION_SLACK = "slack"
    ACTION_DISCORD = "discord"
    ACTION_TELEGRAM = "telegram"
    
    # Project Management
    ACTION_JIRA = "jira"
    ACTION_ASANA = "asana"
    ACTION_MONDAY = "monday"
    
    # CRM
    ACTION_SALESFORCE = "salesforce"
    ACTION_HUBSPOT = "hubspot"
    
    # Database
    ACTION_AIRTABLE = "airtable"
    ACTION_MONGODB = "mongodb"
    
    # Logic
    LOGIC_CONDITION = "condition"
    LOGIC_LOOP = "loop"
    LOGIC_DELAY = "delay"

# Piece Configuration Models
class ManualTriggerConfig(BaseModel):
    pass

class WebhookTriggerConfig(BaseModel):
    url: Optional[str] = None

class ScheduleTriggerConfig(BaseModel):
    cron: Optional[str] = None

class GmailSendConfig(BaseModel):
    receiver: List[str] = Field(description="Receiver Email (To) (one per line)")
    cc: Optional[List[str]] = Field(default=None, description="CC Email (one per line)")
    bcc: Optional[List[str]] = Field(default=None, description="BCC Email (one per line)")
    subject: str = Field(description="Subject of the email")
    body_type: Literal["plain_text", "html"] = Field(default="plain_text", description="Body Type")
    body: str = Field(description="Body for the email you want to send")
    reply_to: Optional[List[str]] = Field(default=None, description="Reply-To Email (one per line)")
    sender_name: Optional[str] = Field(default=None, description="Sender Name")
    from_email: Optional[str] = Field(default=None, description="Sender Email (must be listed in your Gmail settings)")
    draft: bool = Field(default=False, description="Create draft without sending")

class GmailReadConfig(BaseModel):
    folder: str = Field(default="inbox", description="Folder to read from")
    status_filter: Literal["ALL", "UNSEEN", "SEEN"] = Field(default="ALL", description="Filter by status")
    sender_email: Optional[str] = Field(default=None, description="Only read emails from this sender")
    days_ago: Optional[int] = Field(default=None, description="Only read emails received in the last X days")
    limit: int = Field(default=10, description="Max number of emails to read (1-100)")

class GmailSearchConfig(BaseModel):
    from_email: Optional[str] = Field(default=None, description="Sender email address")
    to_email: Optional[str] = Field(default=None, description="Recipient email address")
    subject: Optional[str] = Field(default=None, description="Search by subject")
    content: Optional[str] = Field(default=None, description="Search for specific text within email body")
    has_attachment: bool = Field(default=False, description="Only find emails with attachments")
    attachment_name: Optional[str] = Field(default=None, description="Search for emails with specific attachment filename")
    label: Optional[str] = Field(default=None, description="Search by label name")
    category: Optional[str] = Field(default=None, description="Search by category (e.g. primary, promotions, social)")
    after_date: Optional[str] = Field(default=None, description="Find emails sent after this date (YYYY-MM-DD)")
    before_date: Optional[str] = Field(default=None, description="Find emails sent before this date (YYYY-MM-DD)")
    include_spam_trash: bool = Field(default=False, description="Include emails from Spam and Trash folders in search results")
    max_results: int = Field(default=10, description="Maximum number of emails to return (1-500)")

class SlackConfig(BaseModel):
    webhook_url: str
    message: str
    channel: Optional[str] = None

class DiscordConfig(BaseModel):
    webhook_url: str
    message: str

class TelegramConfig(BaseModel):
    chat_id: str
    message: str

class JiraConfig(BaseModel):
    project_key: str
    issue_type: str = "Task"
    summary: str
    description: Optional[str] = None

class AsanaConfig(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None

class MondayConfig(BaseModel):
    board_id: str
    item_name: str

class SalesforceConfig(BaseModel):
    object_type: str
    fields: Dict[str, Any]

class AirtableConfig(BaseModel):
    table_id: str
    fields: Dict[str, Any]

class ConditionConfig(BaseModel):
    condition: str

class LoopConfig(BaseModel):
    loop_type: Literal["Array / Object", "Number"] = Field(
        default="Array / Object",
        description="Type of loop to perform"
    )
    array_field: str = Field(
        default="", 
        description="Array/Dictionary to iterate over (e.g. {{step_1.output}})"
    )
    number_iterations: int = Field(
        default=5,
        description="Number of times to loop (if Number loop type is selected)"
    )

class DelayConfig(BaseModel):
    duration_seconds: int

class ServiceNowCreateConfig(BaseModel):
    short_description: str = Field(description="Summary of the incident")
    description: Optional[str] = Field(default=None, description="Detailed description")
    urgency: Optional[str] = Field(default="3", description="1-High, 2-Medium, 3-Low")
    severity: Optional[str] = Field(default="3", description="1-High, 2-Medium, 3-Low")

class ServiceNowUpdateConfig(BaseModel):
    sys_id: str = Field(description="Sys ID of the incident to update")
    state: str = Field(description="State to update to (e.g., 1, 2, 3)")
    comments: Optional[str] = Field(default=None, description="Additional comments")

class ServiceNowGetConfig(BaseModel):
    limit: int = Field(default=5, description="Number of incidents to return")
    state: Optional[str] = Field(default=None, description="Filter by state")

class ServiceNowQueryConfig(BaseModel):
    table_name: str = Field(default="incident", description="Name of the ServiceNow table")
    query: Optional[str] = Field(default=None, description="Encoded query string")
    limit: int = Field(default=5, description="Number of records to return")

class SalesforceCreateConfig(BaseModel):
    object_type: str = Field(description="API Name of the object (e.g. Account, Contact)")
    data: Dict[str, Any] = Field(description="JSON dictionary of fields to set")

class SalesforceQueryConfig(BaseModel):
    query: str = Field(description="SOQL Query string")

class AIAgentConfig(BaseModel):
    agent_id: int = Field(description="ID of the AI Agent to query")
    query: str = Field(description="The prompt or question to ask the agent")

# Piece Definitions for Frontend
class PieceDefinition(BaseModel):
    name: str
    displayName: str
    category: str
    description: str = Field(default="")
    icon: Optional[str] = None
    requiredFields: List[str] = Field(default_factory=list)
    optionalFields: List[str] = Field(default_factory=list)

def get_node_catalog() -> List[PieceDefinition]:
    return [
        # Triggers
        PieceDefinition(name="manual", displayName="Manual Trigger", category="Triggers", description="Start your workflow manually."),
        PieceDefinition(name="webhook", displayName="Webhook Trigger", category="Triggers", description="Trigger from external webhooks.", requiredFields=["url"]),
        PieceDefinition(name="schedule", displayName="Schedule Trigger", category="Triggers", description="Run the workflow on a schedule.", requiredFields=["cron"]),
        
        # Logic
        PieceDefinition(name="logic_loop", displayName="For Each Loop", category="Logic", description="Iterate over a list of items.", requiredFields=["items"]),
        PieceDefinition(name="condition", displayName="If/Else Condition", category="Logic", description="Branch workflow execution.", requiredFields=["condition"]),
        PieceDefinition(name="delay", displayName="Delay/Wait", category="Logic", description="Pause execution for a time.", requiredFields=["duration_seconds"]),
        
        # Connectors (Email, CRM, etc mapped to Connectors for UI consistency)
        PieceDefinition(name="gmail_send_email", displayName="Send Email (Gmail)", category="Gmail Suite", icon="https://cdn.worldvectorlogo.com/logos/gmail-icon.svg", description="Send email via Gmail.", requiredFields=["email_to", "subject", "body"]),
        PieceDefinition(name="gmail_read_email", displayName="Read Email (Gmail)", category="Gmail Suite", icon="https://cdn.worldvectorlogo.com/logos/gmail-icon.svg", description="Read emails from Gmail.", requiredFields=["folder"]),
        PieceDefinition(name="gmail_search_email", displayName="Search Email (Gmail)", category="Gmail Suite", icon="https://cdn.worldvectorlogo.com/logos/gmail-icon.svg", description="Search emails in Gmail.", requiredFields=["query"]),
        PieceDefinition(name="slack", displayName="Slack", category="Slack", icon="https://upload.wikimedia.org/wikipedia/commons/d/d5/Slack_icon_2019.svg", description="Send messages to Slack.", requiredFields=["webhook_url", "message"]),
        PieceDefinition(name="jira", displayName="Jira", category="Atlassian Jira", icon="https://cdn.worldvectorlogo.com/logos/jira-1.svg", description="Create Jira issues.", requiredFields=["project_key", "summary"]),
        
        PieceDefinition(name="airtable", displayName="Airtable", category="Airtable", icon="https://upload.wikimedia.org/wikipedia/commons/4/4b/Airtable_Logo.svg", description="Create or update Airtable records.", requiredFields=["table_id", "fields"]),
        PieceDefinition(name="salesforce_create", displayName="Create Record (Salesforce)", category="Salesforce CRM", icon="https://cdn.worldvectorlogo.com/logos/salesforce-2.svg", description="Create a new Salesforce record.", requiredFields=["object_type", "data"]),
        PieceDefinition(name="salesforce_query", displayName="Query SOQL (Salesforce)", category="Salesforce CRM", icon="https://cdn.worldvectorlogo.com/logos/salesforce-2.svg", description="Execute a SOQL query.", requiredFields=["query"]),
        PieceDefinition(name="servicenow_create_incident", displayName="Create Incident (ServiceNow)", category="ServiceNow", icon="https://upload.wikimedia.org/wikipedia/commons/5/57/ServiceNow_logo.svg", description="Create a new incident.", requiredFields=["short_description"]),
        PieceDefinition(name="servicenow_update_incident", displayName="Update Incident (ServiceNow)", category="ServiceNow", icon="https://upload.wikimedia.org/wikipedia/commons/5/57/ServiceNow_logo.svg", description="Update an existing incident.", requiredFields=["sys_id", "state"]),
        PieceDefinition(name="servicenow_get_incidents", displayName="Get Incidents (ServiceNow)", category="ServiceNow", icon="https://upload.wikimedia.org/wikipedia/commons/5/57/ServiceNow_logo.svg", description="Fetch latest incidents.", requiredFields=["limit"]),
        PieceDefinition(name="servicenow_query_table", displayName="Query Table (ServiceNow)", category="ServiceNow", icon="https://upload.wikimedia.org/wikipedia/commons/5/57/ServiceNow_logo.svg", description="Search any table.", requiredFields=["table_name", "limit"]),
        PieceDefinition(name="ai_agent", displayName="Ask AI Agent", category="Logic", description="Pass a query to an AI Agent.", requiredFields=["agent_id", "query"]),
    ]

NODE_CONFIG_MAP = {
    "logic_loop": LoopConfig,
    "manual": ManualTriggerConfig,
    "webhook": WebhookTriggerConfig,
    "schedule": ScheduleTriggerConfig,
    "gmail": GmailSendConfig,
    "gmail_send_email": GmailSendConfig,
    "gmail_read_email": GmailReadConfig,
    "gmail_search_email": GmailSearchConfig,
    "smtp": GmailSendConfig,
    "slack": SlackConfig,
    "discord": DiscordConfig,
    "telegram": TelegramConfig,
    "jira": JiraConfig,
    "asana": AsanaConfig,
    "monday": MondayConfig,
    
    "airtable": AirtableConfig,
    "condition": ConditionConfig,
    "loop": LoopConfig,
    "delay": DelayConfig,
    "salesforce_create": SalesforceCreateConfig,
    "salesforce_query": SalesforceQueryConfig,
    "servicenow_create_incident": ServiceNowCreateConfig,
    "servicenow_update_incident": ServiceNowUpdateConfig,
    "servicenow_get_incidents": ServiceNowGetConfig,
    "servicenow_query_table": ServiceNowQueryConfig,
    "ai_agent": AIAgentConfig,
}


def get_piece_schema(piece_name: str) -> Optional[Dict[str, Any]]:
    """Get JSON schema for a piece configuration"""
    config_model = NODE_CONFIG_MAP.get(piece_name)
    if not config_model:
        return None
    
    return config_model.model_json_schema()


def get_all_piece_schemas() -> Dict[str, Dict[str, Any]]:
    """Get all piece schemas with their definitions"""
    schemas = {}
    for piece_name, config_model in NODE_CONFIG_MAP.items():
        schemas[piece_name] = {
            "schema": config_model.model_json_schema(),
            "definition": next((p for p in get_node_catalog() if p.name == piece_name), None)
        }
    return schemas
