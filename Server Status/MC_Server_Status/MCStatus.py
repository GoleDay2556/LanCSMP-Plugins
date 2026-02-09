import requests
import socket
import time
import json
import sys
import os

VERSION = "V1.4MC"
CONFIG_FILE = "config.json"

# ---- COLORS ----
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
# ----------------

config = None

def load_config():
    global config

    if not os.path.exists(CONFIG_FILE):
        print(RED + "❌ Error1: .jsonFileMissing" + RESET)
        return False

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return True
    except Exception:
        print(RED + "❌ Error2: WrongConfig" + RESET)
        return False

# Load config
if not load_config():
    while True:
        time.sleep(60)

# Validate required keys
required_keys = [
    "statuspage_api_key",
    "page_id",
    "component_id",
    "mc_host",
    "status_profile"
]

for key in required_keys:
    if key not in config:
        print(RED + "❌ Error2: WrongConfig" + RESET)
        while True:
            time.sleep(60)

STATUSPAGE_API_KEY = config["statuspage_api_key"]
PAGE_ID = config["page_id"]
COMPONENT_ID = config["component_id"]

MC_HOST = config["mc_host"]
MC_PORT = config.get("mc_port", 25565)
CHECK_INTERVAL = config.get("check_interval", 60)
STATUS_PROFILE = config["status_profile"]

# ---- AUTH TEST ----
def test_auth():
    url = f"https://api.statuspage.io/v1/pages/{PAGE_ID}"
    headers = {
        "Authorization": f"Bearer {STATUSPAGE_API_KEY}"
    }
    r = requests.get(url, headers=headers)

    print(f"DEBUG → Auth test HTTP {r.status_code}")

    if r.status_code in (200, 304):
        print(GREEN + "✅ Bearer Connection success" + RESET)
        return True
    elif r.status_code == 401:
        print(RED + "❌ Error3: Invalid API Key" + RESET)
    elif r.status_code == 404:
        print(RED + "❌ Error4: Wrong Page ID" + RESET)
    else:
        print(RED + f"❌ Error: HTTP {r.status_code}" + RESET)

    return False

if not test_auth():
    while True:
        time.sleep(60)

# ------------------

def is_server_online():
    try:
        sock = socket.create_connection((MC_HOST, MC_PORT), timeout=5)
        sock.close()
        return True
    except:
        return False

def update_status(status):
    url = f"https://api.statuspage.io/v1/pages/{PAGE_ID}/components/{COMPONENT_ID}"
    headers = {
        "Authorization": f"Bearer {STATUSPAGE_API_KEY}"
    }
    data = {
        "component[status]": status
    }
    r = requests.patch(url, headers=headers, data=data)
    print("========== Status ==========")
    print(YELLOW + f"Status → {status} ({r.status_code})" + RESET)


print(GREEN + "✅ MC Status Loaded! " + VERSION + RESET)

while True:
    update_status("operational" if is_server_online() else STATUS_PROFILE)
    time.sleep(CHECK_INTERVAL)
