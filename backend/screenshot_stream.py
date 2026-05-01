#!/usr/bin/env python3
"""
🐉 直播截圖服務
Playwright → CDP → 每3秒截圖 → backend static/
"""
import subprocess, json, time, sys, os, base64
from datetime import datetime

PLAYWRIGHT_CODE = """
const {{ chromium }} = require('playwright');
const fs = require('fs');

(async () => {{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const context = await browser.newContext();
  const page = await context.newPage();
  
  await page.goto('https://mrtopanclaw-alt.github.io/dragon-console/game.html');
  await page.waitForTimeout(2000);
  
  let count = 0;
  while (count < 9999) {{
    try {{
      const path = '/home/mr-t/dragon-game/backend/static/live.jpg';
      await page.screenshot({{ path, type: 'jpeg', quality: 60 }});
      console.log('SNAP:' + Date.now());
    }} catch(e) {{
      console.error('ERR:' + e.message);
    }}
    await page.waitForTimeout(3000);
    count++;
  }}
}})();
"""

def write_code():
    os.makedirs('/home/mr-t/dragon-game/backend/static', exist_ok=True)
    with open('/tmp/live_capture.js', 'w') as f:
        f.write(PLAYWRIGHT_CODE)
    print("Script written")

def start():
    write_code()
    print("Starting screenshot capture...")
    sys.stdout.flush()
    proc = subprocess.Popen(
        ['node', '/tmp/live_capture.js'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    for line in proc.stdout:
        print(line.decode().strip())

if __name__ == '__main__':
    start()
