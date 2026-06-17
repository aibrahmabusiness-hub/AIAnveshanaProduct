from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    logs = []
    page.on("console", lambda msg: logs.append(f"CONSOLE {msg.type}: {msg.text}"))
    page.on("pageerror", lambda err: logs.append(f"ERROR: {err}"))
    
    page.goto('http://localhost:8000/login')
    page.evaluate("localStorage.setItem('token', 'dummy-token');")
    
    # Try navigating to a mock project
    page.goto('http://localhost:8000/project/11')
    
    page.wait_for_timeout(3000)
    
    # Try clicking tools
    try:
        page.click('.ws-nav-item[data-view="tools"]')
        page.wait_for_timeout(2000)
    except Exception as e:
        logs.append(f"CLICK ERROR: {e}")
        
    for log in logs:
        print(log)
        
    browser.close()
