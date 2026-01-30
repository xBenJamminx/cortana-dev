const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  
  await page.goto('http://localhost:8000');
  await page.waitForTimeout(1500);
  
  // Skills page
  await page.click('[data-page="skills"]');
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'screenshots/v4-skills.png' });
  
  // Schedules page  
  await page.click('[data-page="schedules"]');
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'screenshots/v4-schedules.png' });
  
  // Pipeline page
  await page.click('[data-page="pipeline"]');
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'screenshots/v4-pipeline.png' });
  
  // Channels page
  await page.click('[data-page="channels"]');
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'screenshots/v4-channels.png' });
  
  await browser.close();
})();
