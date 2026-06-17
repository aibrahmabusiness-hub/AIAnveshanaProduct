import sys

with open('frontend/project.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add ID to the card
target_card = '                        <div class="agent-hub-card split-card">\n                            <div class="split-top" style="color: var(--orange-primary);">'
replaced_card = '                        <div class="agent-hub-card split-card" id="createFromPromptBtn" style="cursor:pointer;">\n                            <div class="split-top" style="color: var(--orange-primary);">'
if target_card in text:
    text = text.replace(target_card, replaced_card, 1)

# 2. Add Modal
modal_code = """
    <!-- Create Agent from Prompt Modal -->
    <div class="modal-overlay" id="agentPromptModal">
        <div class="modal" style="width:600px;">
            <div class="modal-header">
                <h3>Create Agent from Prompt</h3>
                <button class="close-btn" id="closeAgentPromptModalBtn">&times;</button>
            </div>
            <div style="padding: 24px;">
                <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:16px;">Describe the agent you want to create in plain English. Our AI will automatically configure the optimal role, goals, and system prompt for it.</p>
                <form id="agentPromptForm" style="display:flex; flex-direction:column; gap:16px;">
                    <div class="form-group" style="margin-bottom:0;">
                        <textarea id="agentIntentInput" rows="5" placeholder="e.g. I need an agent that reviews pull requests, identifies security vulnerabilities, and summarizes the code changes in a structured markdown format." required style="width:100%; padding:12px; border:1px solid var(--border-color); border-radius:8px; font-family:inherit; resize:vertical;"></textarea>
                    </div>
                    <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:8px;">
                        <button type="submit" class="btn-primary" id="generateAgentBtn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:6px; display:inline-block; vertical-align:middle;"><path d="m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72Z"></path><path d="m14 7 3 3"></path><path d="M5 6v4"></path><path d="M19 14v4"></path><path d="M10 2v2"></path><path d="M7 8H3"></path><path d="M21 16h-4"></path><path d="M11 3H9"></path></svg>
                            Generate Agent
                        </button>
                    </div>
                </form>
                <div id="agentGenLoading" style="display:none; text-align:center; padding: 20px; color: var(--text-muted); font-size: 0.9rem;">
                    <div class="spinner" style="margin: 0 auto 10px; width:24px; height:24px; border:3px solid var(--border-color); border-top-color:var(--primary-color); border-radius:50%; animation: spin 1s linear infinite;"></div>
                    Generating intelligent agent... This may take up to 30 seconds.
                    <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
                </div>
            </div>
        </div>
    </div>
"""

target_end = '    <script src="/project.js"></script>'
if target_end in text:
    text = text.replace(target_end, modal_code + '\n' + target_end)

with open('frontend/project.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("project.html patched for agent generation.")
