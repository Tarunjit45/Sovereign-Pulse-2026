import os
import json
import base64
import requests
from datetime import datetime, timezone, timedelta

TOKEN = os.getenv("GITHUB_TOKEN")
USER = os.getenv("GITHUB_USERNAME") 
REPO = os.getenv("GITHUB_REPO")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

IST = timezone(timedelta(hours=5, minutes=30))

def get_ai_insight():
    """Ask OpenRouter for a unique AI micro-trend (no Playwright needed)."""
    if not OPENROUTER_KEY:
        return f"[{datetime.now(IST).strftime('%H:%M')}] System pulse active."
    
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
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
        print(f"OpenRouter error: {e}")
    
    return "Autonomous AI agents continue reshaping developer workflows in 2026."

def update_file(path, content, message):
    """Create or update a file on GitHub."""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{path}"
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
    """Push a unique micro-research log every hour."""
    now = datetime.now(IST)
    insight = get_ai_insight()
    entry = f"[{now.strftime('%Y-%m-%d %H:%M IST')}] {insight}"
    
    # Get existing content
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/PULSE_ACTIVITY.txt"
    r = requests.get(url, headers=HEADERS)
    existing = ""
    if r.status_code == 200:
        existing = base64.b64decode(r.json()["content"]).decode("utf-8")
    
    new_content = existing.rstrip() + "\n" + entry + "\n"
    
    success = update_file(
        "PULSE_ACTIVITY.txt",
        new_content,
        f"\U0001f7e2 Pulse: {now.strftime('%H:%M IST')} - {insight[:40]}..."
    )
    print(f"{'\u2705' if success else '\u274c'} Hourly Pulse: {entry[:60]}...")

def daily_dashboard():
    """Build full Mission Dashboard (runs at ~08:00 IST)."""
    now = datetime.now(IST)
    insight = get_ai_insight()
    
    dashboard = f"""# \u26a1 Project Sovereign-OS-2026: Mission Dashboard

**Last Updated:** {now.strftime('%Y-%m-%d %H:%M:%S')} IST

## \U0001f52d AI Trend of the Day
{insight}

## \U0001f50d System Status
- **Cloud Vessel:** ONLINE (GitHub Actions)
- **Pulse Frequency:** Every 60 minutes  
- **Brain:** OpenRouter (Free Tier)
- **Integrity:** All systems nominal

## \U0001f4ca Activity Metrics
- **Daily Contributions Target:** 24
- **Automation Level:** 100% (Cloud-Native)

---
*Generated autonomously by Project Sovereign-OS-2026 (Cloud Vessel)*
"""
    
    success = update_file(
        "MISSION_DASHBOARD.md",
        dashboard,
        f"\U0001f916 Daily Dashboard: {now.strftime('%Y-%m-%d')}"
    )
    print(f"{'\u2705' if success else '\u274c'} Daily Dashboard updated.")

if __name__ == "__main__":
    print(f"\U0001f680 [Cloud-Vessel] Waking up at {datetime.now(IST).strftime('%Y-%m-%d %H:%M IST')}")
    
    # Always run hourly pulse
    hourly_pulse()
    
    # Run dashboard update around 02:00-03:00 UTC (~07:30-08:30 IST)
    utc_hour = datetime.utcnow().hour
    if utc_hour in [2, 3]:
        daily_dashboard()
    
    print("\u2705 [Cloud-Vessel] Mission complete. Going back to sleep.")
