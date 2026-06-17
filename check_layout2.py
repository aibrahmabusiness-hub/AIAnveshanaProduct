from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto('http://localhost:8000/login')
    page.evaluate("localStorage.setItem('token', 'dummy-token');")
    page.goto('http://localhost:8000/project.html')
    
    page.wait_for_selector('.ws-nav-item[data-view="tools"]', timeout=10000)
    page.click('.ws-nav-item[data-view="tools"]')
    page.wait_for_timeout(2000)
    page.screenshot(path='c:/Users/Admin/.gemini/antigravity-ide/brain/4dbd022e-753a-46f8-89b1-4a7dc5dbb9bf/tools_layout_check.png')
    browser.close()
