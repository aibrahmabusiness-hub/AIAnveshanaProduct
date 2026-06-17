import sys

with open('frontend/project.html', 'r', encoding='utf-8') as f:
    text = f.read()

modal_code = """
    <!-- Integration Auth Modal -->
    <div class="modal-overlay" id="integrationAuthModal">
        <div class="modal" style="width:500px;">
            <div class="modal-header">
                <h3 id="integrationAuthModalTitle">Connect Integration</h3>
                <button class="close-btn" id="closeIntegrationAuthModalBtn">&times;</button>
            </div>
            <div style="padding: 24px;" id="integrationAuthModalBody">
                <!-- Dynamic form gets appended here -->
            </div>
            <div style="padding: 16px 24px; border-top: 1px solid var(--border-color); display:flex; justify-content:flex-end; gap:12px; background:#f8fafc; border-radius: 0 0 12px 12px;">
                <button type="button" class="btn-cancel" id="integrationAuthTestBtn">Test Connection</button>
                <button type="button" class="btn-primary" id="integrationAuthSaveBtn">Save Connection</button>
            </div>
            <div id="integrationAuthModalStatus" style="padding: 16px 24px; display:none; font-size:0.85rem;"></div>
        </div>
    </div>
"""

if 'id="integrationAuthModal"' not in text:
    text = text.replace('<!-- Create Agent from Prompt Modal -->', modal_code + '\n    <!-- Create Agent from Prompt Modal -->')

with open('frontend/project.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("integrationAuthModal injected into project.html")
