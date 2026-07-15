const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', error => console.log('BROWSER ERROR:', error.message));
  
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(1000);
  
  // Try to click Test 1
  try {
    const test1Btn = await page.$('text=Test 1: Thermal Multi-Tile NPD');
    if (test1Btn) {
        await test1Btn.click();
        await page.waitForTimeout(500);
        console.log("Clicked Test 1");
    }
  } catch (e) { console.log(e); }

  // Try to click Upload Mode
  try {
    const uploadBtn = await page.$('text=Upload');
    if (uploadBtn) {
        await uploadBtn.click();
        await page.waitForTimeout(500);
        console.log("Clicked Upload");
    }
  } catch (e) { console.log(e); }

  await page.waitForTimeout(1000);
  await browser.close();
})();
