const { chromium } = require('C:\\Users\\BenJammin\\AppData\\Roaming\\npm\\node_modules\\playwright');

async function screenshot(browser, url, outputPath) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  console.log(`Loading: ${url}`);
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  console.log(`Waiting 3s for scripts: ${url}`);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: outputPath, fullPage: true });
  console.log(`Saved: ${outputPath}`);
  await context.close();
}

(async () => {
  const browser = await chromium.launch();
  await Promise.all([
    screenshot(browser, 'https://kaleidoco.webflow.io/v4', 'c:/Projects/cortana-dev/kaleidoco/v4_screenshot.png'),
    screenshot(browser, 'https://kaleidoco.webflow.io/v5', 'c:/Projects/cortana-dev/kaleidoco/v5_screenshot.png'),
    screenshot(browser, 'https://kaleidoco.webflow.io/v6', 'c:/Projects/cortana-dev/kaleidoco/v6_screenshot.png'),
  ]);
  await browser.close();
  console.log('All done!');
})();
