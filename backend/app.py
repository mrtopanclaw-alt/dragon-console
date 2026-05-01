#!/usr/bin/env python3
"""
🐉 黑龍遊戲後端 v2
[網頁] → [Flask] → [密碼驗證] → [直接instantiate Hermes AIAgent]
"""
import os
import sys
import hashlib
import hmac
import logging
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')
app.secret_key = os.urandom(32)

# ── 密碼設定 ──────────────────────────────────────
GAME_PASSWORD = "MrZ.Home"

def verify_password(pwd):
    return hmac.compare_digest(pwd, GAME_PASSWORD)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        pwd = request.headers.get("X-Password", "")
        if not verify_password(pwd):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ── Hermes Agent 延遲載入 ──────────────────────────────────────
_hermes_agent = None

def get_hermes_agent():
    global _hermes_agent
    if _hermes_agent is not None:
        return _hermes_agent

    sys.path.insert(0, '/home/mr-t/hermes-agent-new')
    os.environ.setdefault('MINIMAX_API_KEY', os.environ.get('MINIMAX_API_KEY', ''))

    from run_agent import AIAgent

    _hermes_agent = AIAgent(
        base_url="https://api.minimax.io/v1",
        api_key=os.environ.get('MINIMAX_API_KEY', ''),
        provider="minimax",
        model="MiniMax-M2.7",
        max_iterations=20,
        enabled_toolsets=["terminal", "file"],
        disabled_toolsets=["browser"],
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
    )
    logging.info("🐉 黑龍 Agent 已初始化")
    return _hermes_agent

# ── 遊戲頁面 ──────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "game.html")

# ── 認證 ──────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    pwd = data.get("password", "")
    if verify_password(pwd):
        return jsonify({"ok": True})
    return jsonify({"error": "Invalid password"}), 401

# ── 遊戲狀態 ──────────────────────────────────────
@app.route("/api/status")
@require_auth
def status():
    return jsonify({
        "hp": 80,
        "ap": 60,
        "status": "待命中",
        "dragon": "🐉 黑龍",
        "online": True
    })

# ── 黑龍對話（核心） ──────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
@require_auth
def chat():
    data = request.get_json() or {}
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Empty message"}), 400

    try:
        agent = get_hermes_agent()
        reply = agent.chat(message)
        return jsonify({"reply": reply or "（黑龍沉默了一會兒...）"})
    except Exception as e:
        logging.error(f"Agent error: {e}")
        return jsonify({"reply": f"⚠️ 黑龍遇到問題：{e}"}), 500

# ── 技能 ──────────────────────────────────────
@app.route("/api/skill/<skill_name>", methods=["POST"])
@require_auth
def use_skill(skill_name):
    skills = {
        "web": "🌐 網頁搜索技能啟動",
        "term": "💻 終端命令技能啟動",
        "file": "📁 文件操作技能啟動",
        "code": "🤖 代碼技能啟動",
        "browser": "🌍 瀏覽器技能啟動",
        "delegate": "👥 委派任務技能啟動"
    }
    msg = skills.get(skill_name, "未知技能")
    return jsonify({"skill": skill_name, "message": msg, "done": True})

# ── 任務列表 ──────────────────────────────────────
@app.route("/api/missions")
@require_auth
def missions():
    return jsonify({
        "missions": [
            {"id": 1, "name": "協調鏈路修復", "priority": "P0", "done": False},
            {"id": 2, "name": "凡龍母體 v2.5 更新", "priority": "P1", "done": False},
            {"id": 3, "name": "遊戲介面製作", "priority": "P2", "done": True}
        ]
    })

# ── 三龍狀態 ──────────────────────────────────────
@app.route("/api/dragons")
@require_auth
def dragons():
    return jsonify({
        "dragons": [
            {"name": "🐉 黑龍", "status": "online", "host": "本地"},
            {"name": "🐲 青龍", "status": "sleep", "host": "本地"},
            {"name": "🐡 金龍", "status": "offline", "host": "VPS"}
        ]
    })

# ── 健康檢查 ──────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print("🐉 黑龍遊戲後端啟動")
    print(f"   密碼: {GAME_PASSWORD}")
    app.run(host="0.0.0.0", port=5177, debug=False)
