#!/home/mr-t/hermes-agent-new/venv/bin/python3
"""
🐉 CDP 截圖擷取器 v3
用 browser-level WS + Target domain 創建新 page target，解決截圖 domain 缺失問題
"""
import json, time, base64, os
import websocket

GAME_URL = "https://mrtopanclaw-alt.github.io/dragon-console/game.html"
OUTPUT_PATH = "/home/mr-t/dragon-game/backend/live.jpg"
INTERVAL = 3  # 秒

BROWSER_WS = "ws://localhost:9222/devtools/browser/c340e4c6-5b45-46fc-9940-8052cdc3040a"

def main():
    print("Connecting to browser-level DevTools...")
    ws = websocket.create_connection(BROWSER_WS, timeout=10)
    print("Connected!")

    cmd_id = [1]  # mutable

    def send(method, params=None, wait_resp=True):
        cmd_id[0] += 1
        msg = {"id": cmd_id[0], "method": method}
        if params:
            msg["params"] = params
        ws.send(json.dumps(msg))
        if wait_resp:
            raw = ws.recv()
            return json.loads(raw)
        return None

    # Target domain: 創建新 page
    print("Creating new page target...")
    resp = send("Target.createTarget", {"url": "about:blank"})
    if "result" not in resp:
        print(f"Error creating target: {resp}")
        ws.close()
        return
    target_id = resp["result"]["targetId"]
    print(f"Created target: {target_id}")

    # 連接新 page 的 WS
    page_ws_url = f"ws://localhost:9222/devtools/page/{target_id}"
    page_ws = websocket.create_connection(page_ws_url, timeout=10)
    print(f"Connected to page WS")

    page_cmd_id = [1]
    def page_send(method, params=None):
        page_cmd_id[0] += 1
        msg = {"id": page_cmd_id[0], "method": method}
        if params:
            msg["params"] = params
        page_ws.send(json.dumps(msg))
        return json.loads(page_ws.recv())

    # 啟用 Page
    print("Enabling Page domain...")
    page_send("Page.enable")

    # 導航
    print(f"Navigating to {GAME_URL}...")
    page_ws.settimeout(20)
    page_send("Page.navigate", {"url": GAME_URL})

    # 等 load
    print("Waiting for Page.loadEventFired...")
    deadline = time.time() + 20
    while time.time() < deadline:
        page_ws.settimeout(max(1, deadline - time.time()))
        try:
            raw = page_ws.recv()
            resp = json.loads(raw)
            if resp.get("method") == "Page.loadEventFired":
                print("Page loaded!")
                break
        except:
            break

    # 持續截圖迴圈
    print(f"Starting screenshot loop (every {INTERVAL}s)...", flush=True)
    count = 0
    try:
        while True:
            count += 1
            ws.settimeout(15)

            # 建立新 target
            resp = send("Target.createTarget", {"url": "about:blank"}, wait_resp=True)
            if "result" not in resp:
                print(f"Target error: {resp}", flush=True)
                break
            target_id = resp["result"]["targetId"]
            page_ws_url = f"ws://localhost:9222/devtools/page/{target_id}"
            page_ws = websocket.create_connection(page_ws_url, timeout=10)

            page_cmd_id = [1]
            def page_send(method, params=None):
                page_cmd_id[0] += 1
                msg = {"id": page_cmd_id[0], "method": method}
                if params: msg["params"] = params
                page_ws.send(json.dumps(msg))
                return json.loads(page_ws.recv())

            page_send("Page.enable")
            page_send("Page.navigate", {"url": GAME_URL})

            # 等 load
            deadline = time.time() + 15
            while time.time() < deadline:
                page_ws.settimeout(max(1, deadline - time.time()))
                try:
                    raw = page_ws.recv()
                    resp = json.loads(raw)
                    if resp.get("method") == "Page.loadEventFired":
                        break
                except:
                    break

            time.sleep(1.5)

            # 截圖 - 需持續讀直到找到 ID 匹配的 response
            screenshot_id = page_cmd_id[0] + 1
            page_ws.send(json.dumps({"id": screenshot_id, "method": "Page.captureScreenshot", "params": {"format": "jpeg", "quality": 60}}))

            result = None
            ss_deadline = time.time() + 15
            while time.time() < ss_deadline:
                page_ws.settimeout(max(1, ss_deadline - time.time()))
                try:
                    raw = page_ws.recv()
                    resp = json.loads(raw)
                    # 忽略 event，只取有 matching ID 的 response
                    if "id" in resp and resp["id"] == screenshot_id:
                        result = resp
                        break
                except:
                    break

            if result and "result" in result and "data" in result["result"]:
                img_data = base64.b64decode(result["result"]["data"])
                with open(OUTPUT_PATH, "wb") as f:
                    f.write(img_data)
                ts = time.strftime("%H:%M:%S")
                print(f"[{ts}] #{count} {len(img_data)} bytes ✅", flush=True)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] #{count} failed: {result}", flush=True)

            page_ws.close()
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print(f"\nStopped after {count} screenshots.", flush=True)
    finally:
        ws.close()

if __name__ == "__main__":
    main()
