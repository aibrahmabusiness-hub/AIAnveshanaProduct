import os
import re

html_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

chat_nav = '''<div class="ws-nav-item" data-view="chat">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                Chat
            </div>
            '''

history_panel = '''
        <!-- Middle: Chat History -->
        <aside class="ws-history" id="historyPanel">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <div class="ws-history-header" style="margin-bottom:0;">Chat Threads</div>
                <button class="btn-primary" id="newThreadBtn" style="padding:4px 8px; font-size:0.75rem; border-radius:4px;">+ New</button>
            </div>
            <div id="historyList" style="display:flex; flex-direction:column; gap:6px;">
                <div style="color:var(--text-muted); font-size:0.85rem; padding:12px 0;">No threads yet. Click "+ New" to start a chat.</div>
            </div>
        </aside>
'''

chat_view = '''
            <!-- Chat View -->
            <div class="ws-view" id="view-chat">
                <div class="ws-chat-container" id="chatContainer">
                    <h1 class="ws-greeting" id="greetingText">What can I help you with?</h1>
                    <div id="chatMessages"></div>
                    <div class="ws-input-box">
                        <input type="text" id="promptInput" placeholder="Ask Anything..." autofocus>
                        <div class="ws-input-actions">
                            <div class="ws-input-tools">
                                <div class="tool-pill" id="connectedToolsBadge">No tools</div>
                            </div>
                            <button class="send-btn" id="sendBtn">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Resizer Handle -->
            <div class="resize-handle" id="resizeHandle"></div>
'''

# 1. Inject chat_nav inside <nav class="ws-sidebar"> right before data-view="agents"
if 'data-view="chat"' not in html:
    html = html.replace('<div class="ws-nav-item active" data-view="agents">', chat_nav + '<div class="ws-nav-item active" data-view="agents">')

# 2. Inject history_panel after </nav>
if 'id="historyPanel"' not in html:
    html = html.replace('</nav>', '</nav>' + history_panel)

# 3. Inject chat_view after <main class="ws-main">
if 'id="view-chat"' not in html:
    html = html.replace('<main class="ws-main">', '<main class="ws-main">' + chat_view)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Restored HTML")
