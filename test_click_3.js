const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    
    // Inject token to bypass login
    await page.goto('http://localhost:8000/');
    await page.evaluate(() => {
        localStorage.setItem('token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEifQ.eyJpZCI6Ik9PdHpHN0R1YjdjRDhFYlVMZjNUUSIsInR5cGUiOiJVU0VSIiwicGxhdGZvcm0iOnsiaWQiOiJ4UGluRHk5akpCdjBOZmhQdGhGelkifSwidG9rZW5WZXJzaW9uIjoiWmJLS0RsVUxsWHhTVjd3bXpYakpEIiwiaWF0IjoxNzgwNTU4NjY4LCJleHAiOjE3ODExNjM0NjgsImlzcyI6ImFjdGl2ZXBpZWNlcyJ9.Ayz2ul5gt1NgPcgJ2iJB2bQIdZuNBuBAQP0OxH2C0nM');
        localStorage.setItem('username', 'test');
    });

    // We must go to the main page where project.js is loaded and wait for the views to set up.
    // The main URL is actually /project.html? Or /project/10?
    // Wait, let's just go to /project/10
    await page.goto('http://localhost:8000/project/10');
    
    await new Promise(r => setTimeout(r, 2000));
    
    console.log("Adding error listener...");
    await page.evaluate(() => {
        window.onerror = function(msg, url, lineNo, columnNo, error) {
            console.log("GLOBAL ERROR:", msg, lineNo, error);
            return false;
        };
    });

    console.log("Clicking workflows tab...");
    // The sidebar item for workflows is:
    await page.evaluate(() => {
        const wfTab = document.querySelector('[data-view="workflows"]');
        if (wfTab) wfTab.click();
    });

    await new Promise(r => setTimeout(r, 1000));

    console.log("Clicking create workflow button...");
    await page.evaluate(() => {
        const btn = document.getElementById('createNewWorkflowBtn');
        if (btn) btn.click();
        else console.log("Button not found!");
    });
    
    await new Promise(r => setTimeout(r, 1000));
    
    await browser.close();
})();
