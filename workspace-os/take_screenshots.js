const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(2500);
    await page.screenshot({ path: 'screenshots/v2-dashboard.png' });
    console.log('Dashboard saved');
    await browser.close();
})();
