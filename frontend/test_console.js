const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on('console', msg => {
    if (msg.type() === 'error') console.log('BROWSER ERROR:', msg.text());
  });
  
  // start vite in background
  const { exec } = require('child_process');
  const vite = exec('npm run dev');
  
  await page.waitForTimeout(3000); // wait for vite
  await page.goto('http://localhost:5173');
  
  await page.waitForTimeout(2000);
  
  // Click export button!
  try {
    await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Export All Plots'));
        if (btn) btn.click();
    });
  } catch(e) {}
  
  await page.waitForTimeout(1000);
  await browser.close();
  vite.kill();
})();
