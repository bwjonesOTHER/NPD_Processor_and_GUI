const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({userDataDir: '/tmp/puppeteer_data'});
  const page = await browser.newPage();
  
  // Capture console messages
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));

  const htmlContent = `
  <!DOCTYPE html>
  <html>
  <head>
    <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
  </head>
  <body>
    <div id="plot" style="width:1200px; height:600px;"></div>
    <script>
      fetch('../../broken.json')
        .then(res => res.json())
        .then(data => {
          console.log('Data loaded, traces:', data.traces.length);
          Plotly.newPlot('plot', data.traces, data.layout).then(() => {
            console.log('Plotly.newPlot resolved successfully');
          }).catch(e => {
            console.error('Plotly error:', e);
          });
        });
    </script>
  </body>
  </html>
  `;
  
  fs.writeFileSync('test_plotly_puppeteer.html', htmlContent);
  
  const fileUrl = 'file://' + process.cwd() + '/test_plotly_puppeteer.html';
  console.log('Navigating to', fileUrl);
  await page.goto(fileUrl);
  
  // Wait a bit for plot to render
  await new Promise(r => setTimeout(r, 2000));
  
  await browser.close();
})();
