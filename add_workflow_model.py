import re
with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_code = '''
class WorkflowCreateRequest(BaseModel):
    agent_id: int
    name: str
    steps: Union[List[Any], Dict[str, Any]]
    status: str = "draft"
'''

if 'class WorkflowCreateRequest' not in content:
    content = content.replace('class WorkflowExecuteRequest(BaseModel):', new_code + '\nclass WorkflowExecuteRequest(BaseModel):')

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
