import sys
import os

# add backend dir to sys.path
sys.path.append(r"c:\Users\Admin\Documents\Agentic AI\backend")

from database import update_agent

try:
    update_agent(
        user_id=1,
        agent_id=1,
        name="Test Agent",
        description="Test Desc",
        system_prompt="Test Sys",
        user_prompt="Test User",
        creativity=0.5,
        guardrails=True,
        max_tool_calls=80,
        llm_config_id=None,
        guardrail_types=["no_competitor_mentions"]
    )
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
