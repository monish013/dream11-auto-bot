import requests
import datetime
import time
import re

BOT_TOKEN = "8501622733:AAFwle-4vd_qPupGrj-xboKwgoa2iBGhurM"
CHAT_ID = "1003800184960"

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

# ---------------- MATCH LIST (AUTO) ----------------
def get_today_matches():
    try:
        url = "https://www.cricbuzz.com/api/html/homepage-scag"
        data = requests.get(url, timeout=10).json()

        matches = []
        for block in data.get("matchList", []):
            for match in block.get("matches", []):
                if match.get("matchStatus") in ["preview", "live"]:
                    matches.append({
                        "id": str(match["matchId"]),
                        "name": f'{match["team1"]["teamName"]} vs {match["team2"]["teamName"]}',
                    })
        return matches
    except:
        return []

# ---------------- TOSS DETECTION ----------------
def detect_toss(match_id):
    try:
        url = f"https://www.cricbuzz.com/api/cricket-match/commentary/{match_id}"
        data = requests.get(url, timeout=10).json()

        for item in data.get("commentaryList", []):
            text = item.get("commText", "")
            if "won the toss" in text.lower():
                return text
    except:
        return None
    return None

# ---------------- TEAM LOGIC ----------------
def generate_team(toss_text):
    chasing = "field" in toss_text.lower() or "bowl" in toss_text.lower()

    if chasing:
        return {
            "strategy": "Chasing-heavy",
            "C": "Top-order Batter",
            "VC": "Batting All-rounder"
        }
    else:
        return {
            "strategy": "Bowling-heavy",
            "C": "Bowling All-rounder",
            "VC": "Death Bowler"
        }

# ---------------- MAIN ----------------
today = datetime.date.today().strftime("%d %b %Y")
send(f"📅 {today}\n🔍 Fetching today’s matches...")

matches = get_today_matches()

if not matches:
    send("❌ No matches found today.")
    exit()

# Send match list
msg = "🏏 TODAY'S MATCHES\n\n"
for m in matches:
    msg += f"• {m['name']} (ID: {m['id']})\n"
send(msg)

# Monitor each match for toss
for match in matches:
    send(f"⏳ Monitoring toss for {match['name']}")

    for _ in range(40):  # ~40 minutes polling
        toss = detect_toss(match["id"])
        if toss:
            team = generate_team(toss)

            final_msg = f"""
🏏 FINAL Dream11 Team (AUTO)

Match: {match['name']}

🪙 Toss Update:
{toss}

📊 Strategy: {team['strategy']}

⭐ Captain: {team['C']}
✨ Vice-Captain: {team['VC']}

⚠️ Fully automated | Free system
"""
            send(final_msg)
            break

        time.sleep(60)
