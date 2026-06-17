import json
with open('C:/Users/Admin/.gemini/antigravity-ide/brain/4dbd022e-753a-46f8-89b1-4a7dc5dbb9bf/.system_generated/logs/transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if 'api/auth/login' in line and '@app.post' in line:
            data = json.loads(line)
            print(data.get('content'))
            print('-------------------')
