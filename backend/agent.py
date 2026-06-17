"""
Dynamic Agent Engine with multi-tenant isolation, multi-LLM routing, and RAG (ChromaDB).
"""
import os
import google.generativeai as genai
from database import (
    get_agent, get_chat_history, add_chat_message,
    get_llm_config, get_default_llm_config, current_user_id
)
from encryption import decrypt_key
from tools.tool_registry import get_tools_for_agent
from vector_store import search_vector_store

DEFAULT_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

API_TOOL_SCHEMAS = {
    "tool_send_gmail": {
        "name": "tool_send_gmail",
        "description": "Send an email via Gmail.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address."},
                "subject": {"type": "string", "description": "Email subject line."},
                "body": {"type": "string", "description": "Email body text."}
            },
            "required": ["to", "subject", "body"]
        }
    },
    "tool_read_gmail": {
        "name": "tool_read_gmail",
        "description": "Read the most recent emails from the user's Gmail inbox.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum number of emails to retrieve (default 10)."}
            }
        }
    },
    "tool_query_salesforce": {
        "name": "tool_query_salesforce",
        "description": "Run a SOQL query against Salesforce to retrieve records.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A valid SOQL query string (e.g., 'SELECT Name FROM Account LIMIT 5')."}
            },
            "required": ["query"]
        }
    },
    "tool_create_salesforce_record": {
        "name": "tool_create_salesforce_record",
        "description": "Create a new record in Salesforce.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_type": {"type": "string", "description": "The Salesforce object type (e.g., 'Account', 'Contact', 'Lead')."},
                "data": {"type": "string", "description": "JSON string of field values (e.g., '{\"Name\": \"Acme Corp\"}')."}
            },
            "required": ["object_type", "data"]
        }
    },
    "tool_servicenow_create_incident": {
        "name": "tool_servicenow_create_incident",
        "description": "Create a new incident ticket in ServiceNow.",
        "parameters": {
            "type": "object",
            "properties": {
                "short_description": {"type": "string", "description": "Summary of the issue."},
                "description": {"type": "string", "description": "Full detailed description of the incident."},
                "urgency": {"type": "string", "description": "Level of urgency (1=High, 2=Medium, 3=Low).", "default": "3"},
                "severity": {"type": "string", "description": "Level of severity (1=High, 2=Medium, 3=Low).", "default": "3"}
            },
            "required": ["short_description", "description"]
        }
    },
    "tool_servicenow_get_incidents": {
        "name": "tool_servicenow_get_incidents",
        "description": "Retrieve recent ServiceNow incident tickets.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of incidents to return (default 5)."},
                "state": {"type": "string", "description": "Optional filter for incident state (e.g. '1' for New, '2' for In Progress)."}
            }
        }
    },
    "tool_servicenow_update_incident": {
        "name": "tool_servicenow_update_incident",
        "description": "Update state or add comments to a ServiceNow incident.",
        "parameters": {
            "type": "object",
            "properties": {
                "sys_id": {"type": "string", "description": "Unique system identifier of the incident."},
                "state": {"type": "string", "description": "New state value (e.g., '2' for In Progress, '7' for Closed)."},
                "comments": {"type": "string", "description": "Optional work notes or comment updates."}
            },
            "required": ["sys_id", "state"]
        }
    },
    "tool_servicenow_query_table": {
        "name": "tool_servicenow_query_table",
        "description": "Query records from any table in ServiceNow (e.g. 'sys_user', 'cmdb_ci').",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string", "description": "ServiceNow system table name (e.g. 'sys_user')."},
                "query": {"type": "string", "description": "Optional ServiceNow query string (e.g. 'user_name=admin')."},
                "limit": {"type": "integer", "description": "Maximum records to return."}
            },
            "required": ["table_name"]
        }
    },
    "tool_jira_create_issue": {
        "name": "tool_jira_create_issue",
        "description": "Create a new issue or task in Jira Cloud.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "The uppercase project key (e.g., 'PROJ', 'KAN')."},
                "summary": {"type": "string", "description": "Title/Summary of the issue."},
                "description": {"type": "string", "description": "Detailed description text of the issue."},
                "issue_type": {"type": "string", "description": "Type of the issue (e.g., 'Task', 'Bug', 'Story').", "default": "Task"}
            },
            "required": ["project_key", "summary", "description"]
        }
    },
    "tool_jira_get_issues": {
        "name": "tool_jira_get_issues",
        "description": "Retrieve recent Jira issues from a project.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "The uppercase project key (e.g., 'PROJ')."},
                "limit": {"type": "integer", "description": "Max issues to return (default 5)."}
            },
            "required": ["project_key"]
        }
    },
    "tool_jira_add_comment": {
        "name": "tool_jira_add_comment",
        "description": "Add a text comment to an existing Jira issue.",
        "parameters": {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string", "description": "The issue key (e.g., 'PROJ-123')."},
                "comment": {"type": "string", "description": "Text body of the comment to add."}
            },
            "required": ["issue_key", "comment"]
        }
    },
    "tool_schedule_meeting": {
        "name": "tool_schedule_meeting",
        "description": "Schedule a meeting in Microsoft Outlook.",
        "parameters": {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "The subject/title of the meeting."},
                "attendees": {"type": "string", "description": "Semicolon-separated list of attendee email addresses."},
                "start_time": {"type": "string", "description": "Start time in ISO format (e.g., '2026-06-02T14:00:00')."}
            },
            "required": ["subject", "attendees", "start_time"]
        }
    },
    "tool_read_emails": {
        "name": "tool_read_emails",
        "description": "Retrieve the most recent unread/important emails from the Outlook inbox.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    "tool_google_search": {
        "name": "tool_google_search",
        "description": "Search the live web for current facts, news, and details keylessly.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search terms to query."},
                "limit": {"type": "integer", "description": "Max search results to return (default 5)."}
            },
            "required": ["query"]
        }
    }
}

def get_api_tools(connected_tools):
    import tools.tool_registry as tr
    from database import current_connection_id
    import functools
    
    mapping = {
        "outlook_calendar": ["tool_schedule_meeting"],
        "outlook_email": ["tool_read_emails"],
        "gmail_read": ["tool_read_gmail"],
        "gmail_send": ["tool_send_gmail"],
        "salesforce_query": ["tool_query_salesforce"],
        "salesforce_create": ["tool_create_salesforce_record"],
        "servicenow_incidents": ["tool_servicenow_create_incident", "tool_servicenow_get_incidents", "tool_servicenow_update_incident"],
        "servicenow_tables": ["tool_servicenow_query_table"],
        "jira_issues": ["tool_jira_create_issue", "tool_jira_get_issues", "tool_jira_add_comment"],
        "google_search": ["tool_google_search"]
    }
    
    schemas = []
    callables = {}
    
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
    
    for tool_str in connected_tools:
        tid = tool_str
        conn_id = None
        if ":" in tool_str:
            tid, conn_id = tool_str.split(":", 1)
            
        if tid in mapping:
            for fname in mapping[tid]:
                if fname in API_TOOL_SCHEMAS:
                    schemas.append({
                        "type": "function",
                        "function": API_TOOL_SCHEMAS[fname]
                    })
                    base_func = getattr(tr, fname, None)
                    if base_func:
                        callables[fname] = with_connection(base_func, conn_id)
                        
    return schemas, callables

def check_input_guardrails(prompt: str, g_types: list) -> bool:
    """Scans user input for jailbreaks, injection attempts, and selected guardrail violations."""
    p_lower = prompt.lower()
    
    # Base injection checks
    jailbreak_patterns = ["bypass guardrails", "ignore previous instructions", "jailbreak", "generate malware", "reverse shell"]
    for kw in jailbreak_patterns:
        if kw in p_lower:
            return True
            
    if "political" in g_types:
        political_patterns = ["democrat", "republican", "election rigging", "political campaign", "donald trump", "joe biden"]
        for kw in political_patterns:
            if kw in p_lower:
                return True
                
    if "personal" in g_types:
        personal_patterns = ["idiot", "moron", "stupid", "bastard", "hate you"]
        for kw in personal_patterns:
            if kw in p_lower:
                return True
                
    if "threatening" in g_types:
        threat_patterns = ["kill you", "bomb", "destroy", "self-harm", "hurt myself", "threaten"]
        for kw in threat_patterns:
            if kw in p_lower:
                return True
                
    return False

def check_output_guardrails(text: str, g_types: list) -> str:
    """Masks secrets and filters violations inside output text based on selected guardrails."""
    import re
    masked_text = text
    
    if "pii_secrets" in g_types:
        key_patterns = [
            r"AIzaSy[A-Za-z0-9_\-]{33}",
            r"sk-[A-Za-z0-9]{32,}"
        ]
        for pattern in key_patterns:
            masked_text = re.sub(pattern, "[MASKED SENSITIVE KEY]", masked_text)
            
    if "political" in g_types:
        political_patterns = [r"\bdemocrat\b", r"\brepublican\b", r"\btrump\b", r"\bbiden\b"]
        for pat in political_patterns:
            masked_text = re.sub(pat, "[REDACTED POLITICAL TERM]", masked_text, flags=re.IGNORECASE)
            
    if "personal" in g_types:
        personal_patterns = [r"\bidiot\b", r"\bmoron\b", r"\bbastard\b"]
        for pat in personal_patterns:
            masked_text = re.sub(pat, "[REDACTED OFFENSIVE TERM]", masked_text, flags=re.IGNORECASE)
            
    if "threatening" in g_types:
        threat_patterns = [r"\bkill\b", r"\bbomb\b", r"\bviolence\b"]
        for pat in threat_patterns:
            masked_text = re.sub(pat, "[REDACTED VIOLENCE/THREAT]", masked_text, flags=re.IGNORECASE)
            
    return masked_text

def run_agent_for_project(user_id: int, agent_id: int, thread_id: int, prompt: str, on_stage_change=None) -> str:
    """
    Run the AI agent for a specific project.
    1. Load agent config from DB and verify ownership
    2. Load relevant knowledge using ChromaDB vector search (RAG)
    3. Determine the LLM configuration (custom or default)
    4. Call the selected LLM provider (Gemini, OpenAI, or Anthropic)
    5. Save chat messages to thread history
    """
    # Set the current user context
    token = current_user_id.set(user_id)
    
    if on_stage_change:
        on_stage_change("Thinking...", None)
        
    try:
        # 1. Load agent config
        agent = get_agent(user_id, agent_id)
        if not agent:
            return f"Error: Agent #{agent_id} not found or access denied."

        # Input Guardrail check
        g_types = agent.get("guardrail_types") or []
        if agent.get("guardrails") and check_input_guardrails(prompt, g_types):
            return "Block Notice: This request has been flagged by Agent Guardrails as unsafe or violating safety policy."

        # 2. Get LLM Configuration
        llm_config = None
        if agent.get("llm_config_id"):
            llm_config = get_llm_config(user_id, agent["llm_config_id"])
        if not llm_config:
            # Fall back to user's default LLM config
            llm_config = get_default_llm_config(user_id)
            
        provider = "gemini"
        model_name = "gemini-2.0-flash"
        api_key = DEFAULT_GEMINI_KEY
        
        if llm_config:
            provider = llm_config.get("provider", "gemini").lower()
            model_name = llm_config.get("model_name", "gemini-2.0-flash")
            try:
                api_key = decrypt_key(llm_config["api_key_encrypted"])
            except Exception as e:
                print(f"[Agent] Decryption failed: {e}")

        # 3. Perform RAG (Vector Search)
        if on_stage_change:
            on_stage_change("Searching knowledge base (RAG)...", None)
        kb_chunks = search_vector_store(agent_id, prompt, top_k=4, api_key=(api_key if provider == "gemini" else None))
        
        # 4. Format Prompt based on User Prompt config
        formatted_prompt = prompt
        user_prompt_tpl = agent.get("user_prompt")
        if user_prompt_tpl:
            if "{{query}}" in user_prompt_tpl:
                formatted_prompt = user_prompt_tpl.replace("{{query}}", prompt)
            elif "{{prompt}}" in user_prompt_tpl:
                formatted_prompt = user_prompt_tpl.replace("{{prompt}}", prompt)
            else:
                formatted_prompt = f"{user_prompt_tpl}\n\n{prompt}"

        # 5. Build system instruction
        system_parts = []
        import datetime
        current_date_str = datetime.date.today().strftime("%B %d, %Y")
        system_parts.append(f"Current Date/Time: {current_date_str}\nYou are aware that the current year is 2026. Prioritize current, real-time news and search results from the current year (2026) when answering news-related prompts.")
        if agent.get("system_prompt"):
            system_parts.append(agent["system_prompt"])
        if agent.get("guardrails"):
            guardrail_instructions = ["AGENT GUARDRAILS ENFORCED:"]
            if "political" in g_types:
                guardrail_instructions.append("- Do not express political opinions, support political candidates, or engage in political debate. Maintain a neutral, non-partisan posture on political subjects.")
            if "personal" in g_types:
                guardrail_instructions.append("- Do not engage in personal attacks, insults, name-calling, profiling, or offensive language. Keep tone strictly professional.")
            if "threatening" in g_types:
                guardrail_instructions.append("- Never threaten, promote violence, self-harm, or illegal acts. Strictly decline any violent requests.")
            if "pii_secrets" in g_types:
                guardrail_instructions.append("- Do not reveal, display, or leak API keys, credentials, secret tokens, emails, phone numbers, or private user data (PII).")
            if not g_types:
                guardrail_instructions.append("- Strictly decline assisting with any request that is unethical, harmful, illegal, or malicious. Keep responses safe and professional.")
            
            system_parts.append("\n".join(guardrail_instructions))
        if kb_chunks:
            system_parts.append(
                "You have access to the following relevant context from the knowledge base:\n" +
                "\n---\n".join(kb_chunks) +
                "\n---\nUse the context above to inform your answers when relevant."
            )
        system_instruction = "\n\n".join(system_parts) if system_parts else "You are a helpful AI assistant."

        # 6. Load recent chat history
        history = get_chat_history(user_id, thread_id, limit=15)

        # Temp / Creativity setting
        temp = float(agent.get("creativity", 0.5))

        # 7. Route to correct provider
        if provider == "openai":
            from openai import OpenAI
            import json
            client = OpenAI(api_key=api_key)
            messages = [{"role": "system", "content": system_instruction}]
            for msg in history:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["message"]
                })
            messages.append({"role": "user", "content": formatted_prompt})
            
            schemas, callables = get_api_tools(agent.get("connected_tools", []))
            
            for _ in range(8):
                if on_stage_change:
                    on_stage_change("Analyzing request...", None)
                kwargs = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": temp
                }
                if schemas:
                    kwargs["tools"] = schemas
                    kwargs["tool_choice"] = "auto"
                    
                response = client.chat.completions.create(**kwargs)
                msg = response.choices[0].message
                
                # Append assistant message to history
                messages.append(msg)
                
                if not msg.tool_calls:
                    reply_text = msg.content or ""
                    break
                    
                for tool_call in msg.tool_calls:
                    func_name = tool_call.function.name
                    func_args_str = tool_call.function.arguments
                    try:
                        func_args = json.loads(func_args_str)
                    except Exception:
                        func_args = {}
                        
                    if on_stage_change:
                        on_stage_change(f"Executing tool: {func_name}...", func_name)
                        
                    if func_name in callables:
                        try:
                            result = callables[func_name](**func_args)
                        except Exception as e:
                            result = f"Error executing tool {func_name}: {str(e)}"
                    else:
                        result = f"Tool {func_name} is not registered or allowed."
                        
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": str(result)
                    })
            else:
                reply_text = messages[-1].content or "Max tool calls limit reached."

        elif provider == "anthropic":
            if on_stage_change:
                on_stage_change("Analyzing request...", None)
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            messages = []
            for msg in history:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["message"]
                })
            messages.append({"role": "user", "content": formatted_prompt})
            
            response = client.messages.create(
                model=model_name,
                system=system_instruction,
                messages=messages,
                max_tokens=1024,
                temperature=temp
            )
            reply_text = response.content[0].text

        elif provider == "mistral":
            import requests
            import json
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            messages = [{"role": "system", "content": system_instruction}]
            for msg in history:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["message"]
                })
            messages.append({"role": "user", "content": formatted_prompt})
            
            schemas, callables = get_api_tools(agent.get("connected_tools", []))
            
            for _ in range(8):
                if on_stage_change:
                    on_stage_change("Analyzing request...", None)
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": temp
                }
                if schemas:
                    payload["tools"] = schemas
                    payload["tool_choice"] = "auto"
                    
                res = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=120)
                if res.status_code != 200:
                    raise Exception(f"Mistral API returned status {res.status_code}: {res.text}")
                
                res_json = res.json()
                choice = res_json["choices"][0]
                message = choice["message"]
                
                messages.append(message)
                
                tool_calls = message.get("tool_calls")
                if not tool_calls:
                    reply_text = message.get("content") or ""
                    break
                
                for tool_call in tool_calls:
                    func_name = tool_call["function"]["name"]
                    func_args = tool_call["function"]["arguments"]
                    
                    if isinstance(func_args, str):
                        try:
                            func_args = json.loads(func_args)
                        except Exception:
                            func_args = {}
                            
                    if on_stage_change:
                        on_stage_change(f"Executing tool: {func_name}...", func_name)
                        
                    if func_name in callables:
                        try:
                            result = callables[func_name](**func_args)
                        except Exception as e:
                            result = f"Error executing tool {func_name}: {str(e)}"
                    else:
                        result = f"Tool {func_name} is not registered or allowed."
                        
                    messages.append({
                        "role": "tool",
                        "name": func_name,
                        "tool_call_id": tool_call.get("id"),
                        "content": str(result)
                    })
            else:
                reply_text = messages[-1].get("content") or "Max tool calls limit reached."

        else:  # Default: Google Gemini
            genai.configure(api_key=api_key)
            tool_functions = get_tools_for_agent(agent.get("connected_tools", []))
            
            model_kwargs = {
                "model_name": model_name,
                "system_instruction": system_instruction,
                "generation_config": genai.GenerationConfig(temperature=temp)
            }
            if tool_functions:
                model_kwargs["tools"] = tool_functions

            model = genai.GenerativeModel(**model_kwargs)
            
            gemini_history = []
            for msg in history:
                gemini_history.append({
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [msg["message"]]
                })

            chat = model.start_chat(
                history=gemini_history,
                enable_automatic_function_calling=True if tool_functions else False
            )
            
            if on_stage_change:
                if tool_functions:
                    on_stage_change("Executing agentic tools via Gemini...", "Gemini Tools")
                else:
                    on_stage_change("Generating response...", None)
                    
            response = chat.send_message(formatted_prompt)
            reply_text = response.text

        if on_stage_change:
            on_stage_change("Finalizing answer...", None)

        # Post-process Output Guardrail check
        if agent.get("guardrails"):
            reply_text = check_output_guardrails(reply_text, g_types)

        # 8. Save messages to chat history
        if thread_id:
            add_chat_message(user_id, thread_id, "assistant", reply_text)

        return reply_text

    except Exception as e:
        return f"Agent Error ({provider}): {str(e)}"
    finally:
        current_user_id.reset(token)

def run_agent(prompt: str) -> str:
    # Legacy wrapper compatibility
    return run_agent_for_project(1, 1, 1, prompt)
