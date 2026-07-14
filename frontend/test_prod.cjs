const puppeteer = require('puppeteer');
const express = require('express');
const app = express();
app.use(express.static('dist'));
const server = app.listen(5002, async () => {
  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
    await page.goto('http://localhost:5002');
    await new Promise(r => setTimeout(r, 2000));
    await browser.close();
  } catch (e) {
    console.error(e);
  } finally {
    server.close();
  }
});
