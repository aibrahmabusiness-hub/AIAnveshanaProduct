const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    // Simulate user login
    await page.goto('http://localhost:8000/login');
    await page.evaluate(() => {
        localStorage.setItem('token', 'dummy');
        localStorage.setItem('username', 'admin');
    });
    await page.goto('http://localhost:8000/project');
    await new Promise(r => setTimeout(r, 2000));
    
    // Add a variable
    await page.evaluate(() => {
        workflowVars.push({ id: 'var_1', name: 'Test', type: 'String', direction: 'input', value: '' });
    });

    // Add Gmail step
    await page.evaluate(() => {
        addWorkflowStep('@activepieces/piece-gmail:send_email');
        showInspector('s2');
    });
    await new Promise(r => setTimeout(r, 1000));

    // Type @ in the first input field
    const input = await page.$('#step-properties-panel input[type="text"]');
    await input.focus();
    await input.type('@');
    await new Promise(r => setTimeout(r, 500));

    const logs = await page.evaluate(() => {
        const d = document.getElementById('at-autocomplete-dropdown');
        if (!d) return 'missing dropdown';
        const display = d.style.display;
        const count = d.children.length;
        const html = d.innerHTML;
        return { display, count, html };
    });
    console.log(JSON.stringify(logs, null, 2));

    await browser.close();
})();
