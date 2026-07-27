import fs from 'fs';
import jsdom from 'jsdom';
const { JSDOM } = jsdom;

const dom = new JSDOM(`<!DOCTYPE html><div id="gd"></div>`);
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;

import Plotly from 'plotly.js-dist-min';
const broken = JSON.parse(fs.readFileSync('../broken.json', 'utf8'));

try {
  console.log('Testing broken.json...');
  Plotly.newPlot(document.getElementById('gd'), broken.traces, broken.layout)
    .then(() => console.log('Success!'))
    .catch(e => console.error('Plotly Async Error:', e));
} catch (e) {
  console.error('Plotly Sync Error:', e);
}
