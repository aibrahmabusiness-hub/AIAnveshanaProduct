const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    // Capture console logs
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
    page.on('requestfailed', request => console.log('REQUEST FAILED:', request.url(), request.failure().errorText));

    await page.goto('http://localhost:8000/login.html');
    
    // login
    await page.type('#username', 'test');
    await page.type('#password', 'test');
    await page.click('button[type="submit"]');
    
    // Wait for redirect to project
    await page.waitForNavigation();
    
    console.log("Navigated to:", page.url());
    
    // wait a bit for scripts to load
    await new Promise(r => setTimeout(r, 2000));
    
    // click create workflow
    console.log("Clicking create workflow button...");
    try {
        await page.click('#createNewWorkflowBtn');
        console.log("Clicked successfully.");
    } catch (e) {
        console.log("Failed to click button:", e.message);
    }
    
    await new Promise(r => setTimeout(r, 2000));
    
    await browser.close();
})();
