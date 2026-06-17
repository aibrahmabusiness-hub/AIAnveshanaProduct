import os
import json
import logging
import asyncio
import httpx
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database import get_conn
from auth import create_access_token

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def execute_workflow_job(workflow_id: int, user_id: int):
    """Fired by APScheduler. Extracts nodes/edges and triggers the workflow via HTTP API."""
    logger.info(f"Cron triggered for workflow {workflow_id}")
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT steps FROM workflows WHERE id = %s AND status = 'active'", (workflow_id,))
        row = cur.fetchone()
        if not row:
            logger.info(f"Workflow {workflow_id} is no longer active. Ignoring cron run.")
            return
            
        steps = row[0]
        if isinstance(steps, str):
            steps = json.loads(steps)
            
        nodes = []
        edges = []
        variables = steps.get("variables", [])
        
        if "drawflow" in steps and "drawflow" in steps["drawflow"]:
            home_data = steps["drawflow"]["drawflow"].get("Home", {}).get("data", {})
            for key, val in home_data.items():
                nodes.append(val)
        elif "nodes" in steps:
            nodes = steps["nodes"]
            edges = steps.get("edges", [])
            
        if not nodes:
            return

        # Mint an admin JWT token for the background job
        token = create_access_token({'sub': 'admin', 'user_id': user_id, 'role': 'superadmin'})
        
        payload = {
            "task_id": f"cron-{workflow_id}-{int(datetime.now().timestamp())}",
            "nodes": nodes,
            "edges": edges,
            "variables": variables,
            "input_data": {"trigger_type": "schedule"}
        }

        # Fire and forget HTTP request to the local API
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            url = f"http://127.0.0.1:8000/api/workflows/{workflow_id}/execute"
            
            # Use background execution so it doesn't block the scheduler thread heavily
            await client.post(url, json=payload, headers=headers, timeout=5.0)
            
    except Exception as e:
        logger.error(f"Failed to execute scheduled workflow {workflow_id}: {e}")
    finally:
        cur.close()
        conn.close()

def load_all_schedules():
    """Loads all active workflows from DB and adds their cron jobs to the scheduler."""
    logger.info("Loading workflow schedules from DB...")
    scheduler.remove_all_jobs()
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, user_id, steps FROM workflows WHERE status = 'active'")
        rows = cur.fetchall()
        count = 0
        for wf_id, user_id, steps_str in rows:
            if not steps_str:
                continue
            steps = json.loads(steps_str) if isinstance(steps_str, str) else steps_str
            
            nodes = []
            if "drawflow" in steps and "drawflow" in steps["drawflow"]:
                home_data = steps["drawflow"]["drawflow"].get("Home", {}).get("data", {})
                nodes = list(home_data.values())
            elif "nodes" in steps:
                nodes = steps["nodes"]
                
            # Find a schedule node
            for node in nodes:
                node_data = node.get("data", {})
                node_type = node_data.get("type", "")
                piece_type = node_data.get("piece", "")
                
                if node_type in ("schedule", "trigger_schedule") or piece_type == "schedule":
                    cron_exp = node_data.get("config", {}).get("cron")
                    if cron_exp:
                        try:
                            # Verify validity of cron string
                            trigger = CronTrigger.from_crontab(cron_exp)
                            scheduler.add_job(
                                execute_workflow_job, 
                                trigger, 
                                args=[wf_id, user_id], 
                                id=f"workflow_{wf_id}",
                                replace_existing=True
                            )
                            count += 1
                        except Exception as e:
                            logger.error(f"Invalid cron '{cron_exp}' for workflow {wf_id}: {e}")
                    break # Only one schedule trigger per workflow supported for now
        logger.info(f"Loaded {count} workflow schedules.")
    except Exception as e:
        logger.error(f"Error loading schedules: {e}")
    finally:
        cur.close()
        conn.close()

def reload_workflow_schedule(workflow_id: int):
    """Reloads the schedule for a single workflow (called on save/update)."""
    # Simply reload everything for safety and simplicity, or just reload the specific one.
    # Since lightweight, reloading all is fine, but reloading specific is safer.
    # For now, we will just call load_all_schedules() since it takes <10ms.
    load_all_schedules()
