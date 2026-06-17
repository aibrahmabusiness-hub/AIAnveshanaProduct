import asyncio
import json
from typing import Dict, Any, List, Set
from graphlib import TopologicalSorter, CycleError
from celery import shared_task
from db import save_execution_history, init_db
import time
import redis.asyncio as aioredis
from datetime import datetime

# Mock handlers for each piece type
async def execute_trigger_manual(config: Dict[str, Any]) -> Dict[str, Any]:
    """Manual trigger - just returns success"""
    return {"success": True, "data": {}}

async def execute_trigger_webhook(config: Dict[str, Any]) -> Dict[str, Any]:
    """Webhook trigger - stores URL for reference"""
    return {"success": True, "url": config.get("url"), "data": {}}

async def execute_trigger_schedule(config: Dict[str, Any]) -> Dict[str, Any]:
    """Schedule trigger - stores cron for reference"""
    return {"success": True, "cron": config.get("cron"), "data": {}}

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def execute_action_gmail(config: Dict[str, Any]) -> Dict[str, Any]:
    """Send Gmail email using smtplib"""
    email_to = config.get("email_to")
    subject = config.get("subject", "No Subject")
    body = config.get("body", "")
    
    if not email_to:
        raise Exception("Missing required field: 'To' (email_to)")

    # For a truly workable node, we try to send via SMTP.
    # If credentials are missing, we mock the success but clearly log the actual intent.
    smtp_user = config.get("smtp_user", "test@example.com")
    smtp_password = config.get("smtp_password", "")
    
    if smtp_password:
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = email_to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Using loop.run_in_executor to avoid blocking the async event loop
            def send_email():
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                server.quit()
            
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, send_email)
            
            return {
                "success": True,
                "message": f"Successfully sent real email to {email_to}",
                "data": {"sent_to": email_to, "subject": subject}
            }
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")
    else:
        # Mock behavior when no credentials are provided (prevent crashing the user's test flow)
        await asyncio.sleep(0.5)
        print(f"[GMAIL MOCK] Sending email to: {email_to} | Subject: {subject} | Body length: {len(body)}")
        return {
            "success": True,
            "message": f"Simulated email sent to {email_to} (Provide SMTP credentials for real sending)",
            "data": {"sent_to": email_to, "subject": subject, "body": body}
        }

async def execute_action_slack(config: Dict[str, Any]) -> Dict[str, Any]:
    """Send Slack message"""
    await asyncio.sleep(0.5)
    return {
        "success": True,
        "message": f"Slack message sent to {config.get('channel', 'default')}",
        "data": {"message": config.get("message")}
    }

async def execute_action_discord(config: Dict[str, Any]) -> Dict[str, Any]:
    """Send Discord message"""
    await asyncio.sleep(0.5)
    return {"success": True, "message": "Discord message sent", "data": {}}

async def execute_action_telegram(config: Dict[str, Any]) -> Dict[str, Any]:
    """Send Telegram message"""
    await asyncio.sleep(0.5)
    return {
        "success": True,
        "message": f"Telegram message sent to {config.get('chat_id')}",
        "data": {}
    }

async def execute_action_jira(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create Jira issue"""
    await asyncio.sleep(1)
    return {
        "success": True,
        "message": f"Jira issue created in {config.get('project_key')}",
        "data": {"issue": f"{config.get('project_key')}-1234", "summary": config.get("summary")}
    }

async def execute_action_asana(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create Asana task"""
    await asyncio.sleep(1)
    return {
        "success": True,
        "message": f"Asana task created: {config.get('name')}",
        "data": {"task_id": "asana_123", "name": config.get("name")}
    }

async def execute_action_monday(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create Monday item"""
    await asyncio.sleep(1)
    return {
        "success": True,
        "message": f"Monday item created: {config.get('item_name')}",
        "data": {"item_id": "monday_456"}
    }

async def execute_action_salesforce(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create Salesforce record"""
    await asyncio.sleep(1)
    return {
        "success": True,
        "message": f"Salesforce {config.get('object_type')} created",
        "data": {"record_id": "sf_789"}
    }

async def execute_action_airtable(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create Airtable record"""
    await asyncio.sleep(1)
    return {
        "success": True,
        "message": f"Airtable record created in {config.get('table_id')}",
        "data": {"record_id": "air_abc"}
    }

async def execute_logic_condition(config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate condition"""
    condition = config.get("condition", "true")
    result = eval(condition) if condition else True
    return {"success": True, "result": result, "data": data}

async def execute_logic_loop(config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute loop"""
    array_field = config.get("array_field", [])
    items = data.get(array_field, []) if isinstance(array_field, str) else []
    return {
        "success": True,
        "iterations": len(items) if isinstance(items, list) else 1,
        "data": data
    }

async def execute_logic_delay(config: Dict[str, Any]) -> Dict[str, Any]:
    """Wait/delay action"""
    duration = config.get("duration_seconds", 1)
    await asyncio.sleep(min(duration, 5))  # Cap at 5 seconds for testing
    return {"success": True, "delayed_seconds": duration, "data": {}}

EXECUTOR_MAP = {
    "manual": execute_trigger_manual,
    "webhook": execute_trigger_webhook,
    "schedule": execute_trigger_schedule,
    "gmail": execute_action_gmail,
    "smtp": execute_action_gmail,
    "slack": execute_action_slack,
    "discord": execute_action_discord,
    "telegram": execute_action_telegram,
    "jira": execute_action_jira,
    "asana": execute_action_asana,
    "monday": execute_action_monday,
    "salesforce": execute_action_salesforce,
    "airtable": execute_action_airtable,
    "condition": execute_logic_condition,
    "loop": execute_logic_loop,
    "delay": execute_logic_delay,
}

def build_execution_order(nodes: List[Dict], edges: List[Dict]) -> List[str]:
    """Build execution order using topological sort"""
    node_ids = [n["id"] for n in nodes]
    
    # Handle case with no edges (independent nodes)
    if not edges:
        return node_ids
    
    sorter = TopologicalSorter()
    
    for node_id in node_ids:
        sorter.add(node_id)
    
    for edge in edges:
        sorter.add(edge["target"], edge["source"])
    
    try:
        return list(sorter.static_order())
    except CycleError:
        raise Exception("Workflow contains circular references")

async def publish_execution_event(redis_url: str, event_type: str, data: Dict[str, Any]):
    """Publish execution event to Redis pub/sub for WebSocket broadcasting"""
    try:
        redis_client = aioredis.from_url(redis_url)
        channel = "workflow_logs"
        message = json.dumps({"type": event_type, "data": data})
        await redis_client.publish(channel, message)
        await redis_client.close()
    except Exception as e:
        print(f"Failed to publish Redis event: {e}")

REDIS_URL = "redis://localhost:6379/0"

@shared_task(bind=True)
def execute_workflow_task(self, workflow_dict: Dict[str, Any]):
    """Execute workflow using Celery with async support and real-time updates"""
    workflow_id = workflow_dict.get("workflow_id", "unknown")
    nodes = workflow_dict.get("nodes", [])
    edges = workflow_dict.get("edges", [])
    
    results = {}
    node_map = {n["id"]: n for n in nodes}
    
    try:
        # Publish workflow start event
        asyncio.run(publish_execution_event(
            REDIS_URL,
            "workflow_start",
            {"workflow_id": workflow_id, "task_id": self.request.id, "node_count": len(nodes)}
        ))
        
        # Build execution order
        execution_order = build_execution_order(nodes, edges)
        
        # Execute nodes in order
        for node_id in execution_order:
            node = node_map.get(node_id)
            if not node:
                continue
            
            piece_type = node.get("data", {}).get("piece")
            config = node.get("data", {}).get("config", {})
            node_label = node.get("data", {}).get("label", node_id)
            
            # Publish node start event
            asyncio.run(publish_execution_event(
                REDIS_URL,
                "node_start",
                {"workflow_id": workflow_id, "node_id": node_id, "node_label": node_label, "piece_type": piece_type}
            ))
            
            executor = EXECUTOR_MAP.get(piece_type)
            
            if executor:
                try:
                    if piece_type in ["condition", "loop"]:
                        result = asyncio.run(executor(config, results))
                    else:
                        result = asyncio.run(executor(config))
                    results[node_id] = result
                    
                    # Publish node success event
                    asyncio.run(publish_execution_event(
                        REDIS_URL,
                        "node_success",
                        {"workflow_id": workflow_id, "node_id": node_id, "result": result}
                    ))
                except Exception as e:
                    error_msg = str(e)
                    results[node_id] = {"success": False, "error": error_msg}
                    
                    # Publish node error event
                    asyncio.run(publish_execution_event(
                        REDIS_URL,
                        "node_error",
                        {"workflow_id": workflow_id, "node_id": node_id, "error": error_msg}
                    ))
            else:
                error_msg = f"Unknown piece type: {piece_type}"
                results[node_id] = {"success": False, "error": error_msg}
                
                # Publish node error event
                asyncio.run(publish_execution_event(
                    REDIS_URL,
                    "node_error",
                    {"workflow_id": workflow_id, "node_id": node_id, "error": error_msg}
                ))
        
        # Save execution history
        started_at = datetime.utcnow().isoformat()
        finished_at = datetime.utcnow().isoformat()
        save_execution_history(
            task_id=self.request.id,
            workflow_id=workflow_id,
            name=f"Execution of {len(nodes)} nodes",
            status="completed",
            results=results,
            started_at=started_at,
            finished_at=finished_at
        )
        
        # Publish workflow complete event
        asyncio.run(publish_execution_event(
            REDIS_URL,
            "workflow_complete",
            {"workflow_id": workflow_id, "task_id": self.request.id, "results": results}
        ))
        
        return {
            "status": "completed",
            "workflow_id": workflow_id,
            "results": results,
            "executed_nodes": len(execution_order)
        }
    
    except Exception as e:
        error_result = {
            "status": "failed",
            "error": str(e),
            "workflow_id": workflow_id
        }
        
        # Publish workflow error event
        asyncio.run(publish_execution_event(
            REDIS_URL,
            "workflow_error",
            {"workflow_id": workflow_id, "task_id": self.request.id, "error": str(e)}
        ))
        
        started_at = datetime.utcnow().isoformat()
        finished_at = datetime.utcnow().isoformat()
        save_execution_history(
            task_id=self.request.id,
            workflow_id=workflow_id,
            name=f"Failed execution",
            status="failed",
            results={"error": str(e)},
            started_at=started_at,
            finished_at=finished_at
        )
        
        return error_result
