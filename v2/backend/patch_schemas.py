import re

filepath = r"c:\Users\Admin\Documents\Agentic AI\v2\backend\schemas.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace ServiceNowConfig with exploded configs
old_servicenow = """class ServiceNowConfig(BaseModel):
    short_description: str
    description: Optional[str] = None
    urgency: Optional[str] = None"""

new_configs = """class ServiceNowCreateConfig(BaseModel):
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
    query: str = Field(description="The prompt or question to ask the agent")"""

if old_servicenow in content:
    content = content.replace(old_servicenow, new_configs)
else:
    print("Could not find ServiceNowConfig in schemas.py!")

# 2. Update get_node_catalog
# Replace the old Salesforce and ServiceNow definitions
old_salesforce_def = 'PieceDefinition(name="salesforce", displayName="Salesforce", category="Connectors", description="Salesforce CRM actions.", requiredFields=["object_type", "fields"]),'
old_servicenow_def = 'PieceDefinition(name="servicenow", displayName="ServiceNow", category="Connectors", description="Create, update, and query ServiceNow incidents.", requiredFields=["short_description"]),'

new_defs = """PieceDefinition(name="salesforce_create", displayName="Create Record (Salesforce)", category="Connectors", description="Create a new Salesforce record.", requiredFields=["object_type", "data"]),
        PieceDefinition(name="salesforce_query", displayName="Query SOQL (Salesforce)", category="Connectors", description="Execute a SOQL query.", requiredFields=["query"]),
        PieceDefinition(name="servicenow_create_incident", displayName="Create Incident (ServiceNow)", category="Connectors", description="Create a new incident.", requiredFields=["short_description"]),
        PieceDefinition(name="servicenow_update_incident", displayName="Update Incident (ServiceNow)", category="Connectors", description="Update an existing incident.", requiredFields=["sys_id", "state"]),
        PieceDefinition(name="servicenow_get_incidents", displayName="Get Incidents (ServiceNow)", category="Connectors", description="Fetch latest incidents.", requiredFields=["limit"]),
        PieceDefinition(name="servicenow_query_table", displayName="Query Table (ServiceNow)", category="Connectors", description="Search any table.", requiredFields=["table_name", "limit"]),
        PieceDefinition(name="ai_agent", displayName="Ask AI Agent", category="Logic", description="Pass a query to an AI Agent.", requiredFields=["agent_id", "query"]),"""

if old_salesforce_def in content:
    content = content.replace(old_salesforce_def, "")
if old_servicenow_def in content:
    content = content.replace(old_servicenow_def, new_defs)

# 3. Update NODE_CONFIG_MAP
old_map_salesforce = '"salesforce": SalesforceConfig,'
old_map_servicenow = '"servicenow": ServiceNowConfig,'

new_map = """"salesforce_create": SalesforceCreateConfig,
    "salesforce_query": SalesforceQueryConfig,
    "servicenow_create_incident": ServiceNowCreateConfig,
    "servicenow_update_incident": ServiceNowUpdateConfig,
    "servicenow_get_incidents": ServiceNowGetConfig,
    "servicenow_query_table": ServiceNowQueryConfig,
    "ai_agent": AIAgentConfig,"""

if old_map_salesforce in content:
    content = content.replace(old_map_salesforce, "")
if old_map_servicenow in content:
    content = content.replace(old_map_servicenow, new_map)


with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("schemas.py updated successfully.")
