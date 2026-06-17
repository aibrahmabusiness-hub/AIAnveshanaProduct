import sys

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Insert button
btn_code = """
                <button class="btn-secondary" id="openGlobalSettingsBtn" style="padding:8px 16px; font-size:0.9rem; display:flex; align-items:center; gap:6px; border:1px solid var(--border-color); border-radius:10px; background:var(--bg-secondary); color:var(--text-main); font-weight:600; cursor:pointer;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                    Global LLM
                </button>
"""
target_btn = '<div class="controls-right" style="display:flex; align-items:center; gap:12px;">'
if target_btn in text:
    text = text.replace(target_btn, target_btn + btn_code)

# Insert modal
modal_code = """
    <!-- Global Settings Modal -->
    <div class="modal-overlay" id="globalSettingsModal">
        <div class="modal" style="width:580px; max-height: 85vh; overflow-y: auto;">
            <div class="modal-header">
                <h3>Global LLM Settings</h3>
                <button class="close-btn" id="closeGlobalSettingsBtn">&times;</button>
            </div>
            <div style="padding: 20px;">
                <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:16px;">Configure global LLM connections that can be used across all your projects.</p>
                <form id="addGlobalLlmForm" style="display:flex; flex-direction:column; gap:12px; margin-bottom:20px;">
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                        <div class="form-group" style="margin-bottom:0;">
                            <label>Provider</label>
                            <select id="globalLlmProvider" style="width:100%; padding:10px; border:1px solid var(--border-color); border-radius:6px; font-family:inherit;">
                                <option value="gemini">Google Gemini</option>
                                <option value="openai">OpenAI</option>
                                <option value="anthropic">Anthropic</option>
                                <option value="mistral">Mistral AI</option>
                            </select>
                        </div>
                        <div class="form-group" style="margin-bottom:0;">
                            <label>Model Name</label>
                            <input type="text" id="globalLlmModel" placeholder="e.g. gpt-4o, gemini-1.5-pro">
                        </div>
                    </div>
                    <div class="form-group" style="margin-bottom:0;">
                        <label>API Key</label>
                        <input type="password" id="globalLlmKey" placeholder="Enter API Key">
                    </div>
                    <div style="display:flex; gap:10px; margin-top:8px;">
                        <button type="submit" class="btn-primary" id="saveGlobalLlmBtn">Add Global LLM</button>
                        <button type="button" id="testGlobalLlmBtn" class="btn-cancel" style="border: 1px solid var(--orange-primary); color: var(--orange-primary); background: none; font-weight:600;">Test Connection</button>
                    </div>
                    <div id="globalLlmTestStatus" style="font-size:0.85rem; padding:8px; border-radius:6px; margin-top:8px; display:none;"></div>
                </form>
                
                <h4>Your Global LLMs</h4>
                <div id="globalLlmConfigsList" style="margin-top:10px; display:flex; flex-direction:column; gap:8px;">
                    <!-- Configs injected here -->
                </div>
            </div>
        </div>
    </div>
"""
target_modal = '<!-- Create Project Modal -->'
if target_modal in text:
    text = text.replace(target_modal, modal_code + '\n    ' + target_modal)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("index.html updated.")
