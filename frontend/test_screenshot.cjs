const puppeteer = require('puppeteer');
const express = require('express');
const app = express();
app.use(express.static('dist'));
const server = app.listen(5003, async () => {
  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto('http://localhost:5003', { waitUntil: 'networkidle0' });
    const html = await page.content();
    console.log("HTML CONTENT:", html);
    await page.screenshot({ path: 'screenshot.png' });
    await browser.close();
  } catch (e) {
    console.error(e);
  } finally {
    server.close();
  }
});
