import os
import base64
import requests
from datetime import datetime, timezone, timedelta

TOKEN = os.getenv("GITHUB_TOKEN")
USER = os.getenv("GITHUB_USERNAME")
REPO = os.getenv("GITHUB_REPO")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

HEADERS = {
    "Authorization": "token " + str(TOKEN),
    "Accept": "application/vnd.github.v3+json"
}

IST = timezone(timedelta(hours=5, minutes=30))

OK = "DONE"
FAIL = "ERROR"

def get_ai_insight():
    if not OPENROUTER_KEY:
        return "System pulse active - no API key configured."
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer " + OPENROUTER_KEY},
            json={
                "model": "openrouter/free",
                "messages": [{"role": "user", "content":
                    "Write ONE short sentence (max 80 chars) about a cutting-edge AI trend in 2026. "
                    "Be specific, mention a real technology or company. No hashtags."}]
            },
            timeout=30
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()[:120]
    except Exception as e:
        print("OpenRouter error: " + str(e))
    return "Autonomous AI agents continue reshaping developer workflows in 2026."

def update_file(path, content, message):
    url = "https://api.github.com/repos/" + USER + "/" + REPO + "/contents/" + path
    r = requests.get(url, headers=HEADERS)
    sha = r.json().get("sha") if r.status_code == 200 else None
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=HEADERS, json=payload)
    return r.status_code in [200, 201]

def hourly_pulse():
    now = datetime.now(IST)
    insight = get_ai_insight()
    timestamp = now.strftime("%Y-%m-%d %H:%M IST")
    entry = "[" + timestamp + "] " + insight

    url = "https://api.github.com/repos/" + USER + "/" + REPO + "/contents/PULSE_ACTIVITY.txt"
    r = requests.get(url, headers=HEADERS)
    existing = ""
    if r.status_code == 200:
        existing = base64.b64decode(r.json()["content"]).decode("utf-8")

    new_content = existing.rstrip() + "\n" + entry + "\n"
    commit_msg = "Pulse: " + timestamp + " - " + insight[:40] + "..."
    success = update_file("PULSE_ACTIVITY.txt", new_content, commit_msg)
    status = OK if success else FAIL
    print("[" + status + "] Hourly Pulse: " + entry[:60] + "...")

def daily_dashboard():
    now = datetime.now(IST)
    insight = get_ai_insight()
    ts = now.strftime("%Y-%m-%d %H:%M:%S")

    dashboard = "# Project Sovereign-OS-2026: Mission Dashboard\n\n"
    dashboard += "**Last Updated:** " + ts + " IST\n\n"
    dashboard += "## AI Trend of the Day\n" + insight + "\n\n"
    dashboard += "## System Status\n"
    dashboard += "- **Cloud Vessel:** ONLINE (GitHub Actions)\n"
    dashboard += "- **Pulse Frequency:** Every 60 minutes\n"
    dashboard += "- **Brain:** OpenRouter (Free Tier)\n"
    dashboard += "- **Integrity:** All systems nominal\n\n"
    dashboard += "## Activity Metrics\n"
    dashboard += "- **Daily Contributions Target:** 24\n"
    dashboard += "- **Automation Level:** 100% (Cloud-Native)\n\n"
    dashboard += "---\n"
    dashboard += "*Generated autonomously by Project Sovereign-OS-2026 (Cloud Vessel)*\n"

    commit_msg = "Daily Dashboard: " + now.strftime("%Y-%m-%d")
    success = update_file("MISSION_DASHBOARD.md", dashboard, commit_msg)
    status = OK if success else FAIL
    print("[" + status + "] Daily Dashboard updated.")

if __name__ == "__main__":
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
    print("[Cloud-Vessel] Waking up at " + now_str)

    hourly_pulse()

    utc_hour = datetime.utcnow().hour
    if utc_hour in [2, 3]:
        daily_dashboard()

    print("[Cloud-Vessel] Mission complete. Going back to sleep.")
