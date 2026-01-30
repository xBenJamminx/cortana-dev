const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  
  console.log('Loading dashboard...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'screenshots/01-dashboard.png', fullPage: true });
  
  // Test Content/Kanban tab
  console.log('Testing Content tab...');
  await page.click('div[data-tab="content"]');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'screenshots/02-content.png', fullPage: true });
  
  // Test Ideas tab
  console.log('Testing Ideas tab...');
  await page.click('div[data-tab="ideas"]');
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'screenshots/03-ideas.png', fullPage: true });
  
  // Test Projects tab
  console.log('Testing Projects tab...');
  await page.click('div[data-tab="projects"]');
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'screenshots/04-projects.png', fullPage: true });
  
  // Test AI tab
  console.log('Testing AI tab...');
  await page.click('div[data-tab="ai"]');
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'screenshots/05-ai.png', fullPage: true });
  
  // Test Performance tab
  console.log('Testing Performance tab...');
  await page.click('div[data-tab="performance"]');
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'screenshots/06-performance.png', fullPage: true });
  
  // Test Memory tab
  console.log('Testing Memory tab...');
  await page.click('div[data-tab="memory"]');
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'screenshots/07-memory.png', fullPage: true });
  
  await browser.close();
  console.log('All screenshots saved!');
})();
