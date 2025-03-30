const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        console.log("Navigating to Gmail signup page...");
        await page.goto('https://accounts.google.com/signup');

        // Explicitly wait longer for dynamic fields (increased timeout)
        await page.waitForSelector('input[name="firstName"]', { timeout: 30000 });

        console.log("Typing into the form fields now...");

        await page.fill('input[name="firstName"]', 'John');
        await page.fill('input[name="lastName"]', 'Doe');

        await page.waitForSelector('input[name="Username"]', { timeout: 30000 });
        await page.fill('input[name="Username"]', 'john.doe.test.1234567');

        await page.fill('input[name="Passwd"]', 'TestPassword123!');
        await page.fill('input[name="ConfirmPasswd"]', 'TestPassword123!');

        console.log("Finished typing!");
        await page.waitForTimeout(10000);

    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        await browser.close();
    }
})();





