const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('https://kaleidoco.webflow.io/v4', { waitUntil: 'networkidle' });
  await page.waitForTimeout(6000);

  // Screenshot of #v4-caps element
  const el = await page.$('#v4-caps');
  if (!el) {
    console.log('ERROR: #v4-caps not found');
  } else {
    await el.screenshot({ path: 'C:/Projects/cortana-dev/kaleidoco/v4_caps.png' });
    console.log('Screenshot saved to v4_caps.png');
  }

  // Count .kc elements inside #v4-caps
  const count = await page.evaluate(() => {
    return document.querySelectorAll('#v4-caps .kc').length;
  });
  console.log('kc count:', count);

  // innerHTML of first .kc inside #v4-caps (first 300 chars)
  const inner = await page.evaluate(() => {
    const firstEl = document.querySelector('#v4-caps .kc');
    return firstEl ? firstEl.innerHTML.substring(0, 300) : 'NOT FOUND';
  });
  console.log('First .kc innerHTML (300 chars):', inner);

  await browser.close();
})();
