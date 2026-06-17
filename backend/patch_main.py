import re

filepath = r"c:\Users\Admin\Documents\Agentic AI\backend\main.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. We need to replace the servicenow block
old_servicenow_pattern = re.compile(r'# ServiceNow\s+elif "servicenow" in tool_name:.*?# Salesforce', re.DOTALL)

new_servicenow = """# ServiceNow
        elif "servicenow" in tool_name:
            from tools.servicenow_tools import create_incident, get_incidents, update_incident, query_table
            if "create" in tool_name or "create" in action_name:
                output = create_incident(
                    short_description=params.get("short_description") or params.get("shortDescription"),
                    description=params.get("description") or params.get("short_description") or "",
                    urgency=params.get("urgency", "3"),
                    severity=params.get("severity", "3")
                )
                return {"success": True, "output": output}
            elif "get" in tool_name or "get" in action_name:
                output = get_incidents(
                    limit=params.get("limit", 5),
                    state=params.get("state")
                )
                return {"success": True, "output": output}
            elif "update" in tool_name or "update" in action_name:
                output = update_incident(
                    sys_id=params.get("sys_id") or params.get("sysId"),
                    state=params.get("state"),
                    comments=params.get("comments")
                )
                return {"success": True, "output": output}
            elif "query" in tool_name or "query" in action_name:
                output = query_table(
                    table_name=params.get("table_name", "incident"),
                    query=params.get("query"),
                    limit=params.get("limit", 5)
                )
                return {"success": True, "output": output}

        # Salesforce"""

if re.search(old_servicenow_pattern, content):
    content = re.sub(old_servicenow_pattern, new_servicenow, content)
else:
    print("Could not find servicenow block")

# 2. We need to replace the salesforce block and append ai_agent
old_salesforce_pattern = re.compile(r'# Salesforce\s+elif "salesforce" in tool_name:.*?# Generic TOOL_REGISTRY fallback', re.DOTALL)

new_salesforce_and_ai = """# Salesforce
        elif "salesforce" in tool_name:
            from tools.salesforce_tools import query_salesforce, create_salesforce_record
            if "query" in tool_name or "query" in action_name:
                output = query_salesforce(query=params.get("query"))
                return {"success": True, "output": output}
            elif "create" in tool_name or "create" in action_name:
                output = create_salesforce_record(
                    object_type=params.get("object_type") or params.get("objectType"),
                    data=params.get("data")
                )
                return {"success": True, "output": output}

        # AI Agent
        elif tool_name == "ai_agent":
            from agent import run_agent_for_project
            agent_id = params.get("agent_id")
            query = params.get("query")
            if not agent_id or not query:
                raise Exception("Missing agent_id or query for AI Agent node")
            output = run_agent_for_project(
                user_id=user_id,
                agent_id=int(agent_id),
                thread_id=0,
                prompt=query
            )
            return {"success": True, "output": output}

        # Generic TOOL_REGISTRY fallback"""

if re.search(old_salesforce_pattern, content):
    content = re.sub(old_salesforce_pattern, new_salesforce_and_ai, content)
else:
    print("Could not find salesforce block")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("main.py updated successfully.")
