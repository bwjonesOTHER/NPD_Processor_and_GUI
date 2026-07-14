const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  await page.goto('http://localhost:4173');
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({path: 'screenshot.png'});
  
  await browser.close();
})();
