import requests
import json
import os

URL = "https://result.doenets.lk/result/service/examDetails"

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

STATE_FILE = "state.json"
OFFSET_FILE = "offset.json"

send("GitHub Action is running", CHAT_ID)

def send(msg, chat_id):
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": chat_id, "text": msg}
    )

def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {}

def save_state(state):
    json.dump(state, open(STATE_FILE, "w"))

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 5}
    if offset:
        params["offset"] = offset
    return requests.get(url, params=params).json()

def load_offset():
    if os.path.exists(OFFSET_FILE):
        return json.load(open(OFFSET_FILE))["offset"]
    return None

def save_offset(offset):
    json.dump({"offset": offset}, open(OFFSET_FILE, "w"))

def check_result():
    data = requests.get(URL, timeout=10).json()
    return {
        "ol": data["desOlResult"],
        "year": data["yearOlResult"]
    }

# ---------------- MAIN ----------------

state = load_state()
offset = load_offset()

updates = get_updates(offset)

for u in updates.get("result", []):
    offset = u["update_id"] + 1

    if "message" in u:
        text = u["message"].get("text", "")
        chat_id = u["message"]["chat"]["id"]

        # COMMAND: /results
        if text == "/results":
            current = check_result()

            status = "❌ NOT RELEASED YET"
            if "Examination" in current["ol"]:
                status = "🚨 STATUS: UPDATED / POSSIBLY RELEASED"

            send(
                f"{status}\n\n"
                f"O/L: {current['ol']}\n"
                f"Year: {current['year']}",
                chat_id
            )

# save offset
if offset:
    save_offset(offset)

# ---------------- AUTO CHECK (15 min part) ----------------

current = check_result()

if not state:
    save_state(current)
    exit()

if current != state:
    send(
        "🚨 RESULTS UPDATED!\n\n"
        f"O/L: {current['ol']}\n"
        f"Year: {current['year']}",
        CHAT_ID
    )
    save_state(current)
