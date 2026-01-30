const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  
  await page.goto('http://localhost:8000');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'screenshots/v5-dashboard.png' });
  
  await page.click('[data-page="twitter"]');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'screenshots/v5-twitter.png' });
  
  await page.click('[data-page="memory"]');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'screenshots/v5-memory.png' });
  
  await page.click('[data-page="pipeline"]');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'screenshots/v5-pipeline.png' });
  
  await browser.close();
})();
