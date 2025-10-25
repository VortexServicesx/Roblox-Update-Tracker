# Made By Avexy

# imports
import requests
import time
import os

# This is a Discord webhook. It does not automatically send messages if your PC, phone, or other device is off. You would need a discord bot to do that.
# Messages are only sent when Roblox updates or when the Python code is executed in your IDE/compiler.

# make sure to replace the WEBHOOK_URL with your webhook URL.

# configs
WEBHOOK_URL = ""  #  replace with your webhook guys.
VERSION_FILE = "roblox_version.txt"
CHECK_INTERVAL = 120


# Roblox binary types
BINARY_TYPES = {
    "Windows": "WindowsPlayer",
    "Mac": "MacPlayer"
}

# version handling shit
def fetch_latest_version(binary_type: str) -> str:
    """Fetch the latest Roblox version for a given binary type (Windows/Mac)."""
    url = f"https://clientsettings.roblox.com/v2/client-version/{binary_type}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    version = data.get("clientVersionUpload")

    if not version:
        raise ValueError(f"No version found for {binary_type}")
    return version


def load_saved_versions() -> dict:
    """Load previously saved versions from the file."""
    if not os.path.exists(VERSION_FILE):
        return {}

    with open(VERSION_FILE, "r") as f:
        lines = f.read().strip().splitlines()

    versions = {}
    for line in lines:
        if "=" in line:
            os_name, version = line.split("=", 1)
            versions[os_name.strip()] = version.strip()
    return versions


def save_versions(versions: dict):
    """Save the current versions to the file."""
    with open(VERSION_FILE, "w") as f:
        for os_name, version in versions.items():
            f.write(f"{os_name}={version}\n")


# discord notify
def send_discord_update(os_name: str, old: str, new: str):
    embed = {
        "title": f"Roblox {os_name} Version Updated",
        "color": 0x5E095E,
        "fields": [
            {"name": "Old Version", "value": f"`{old}`", "inline": True},
            {"name": "New Version", "value": f"`{new}`", "inline": True}
        ],
    }

    data = {"embeds": [embed]}
    requests.post(WEBHOOK_URL, json=data).raise_for_status()


# loop 
def check_for_updates():
    saved_versions = load_saved_versions()
    updated_versions = saved_versions.copy()

    for os_name, binary in BINARY_TYPES.items():
        try:
            latest = fetch_latest_version(binary)
        except Exception as e:
            print(f"Error fetching {os_name} version:", e)
            continue

        old = saved_versions.get(os_name)
        if old is None:
            print(f"[{os_name}] No saved version found. Saving current: {latest}")
            updated_versions[os_name] = latest
        elif latest != old:
            print(f"[{os_name}] Version changed: {old} → {latest}")
            send_discord_update(os_name, old, latest)
            updated_versions[os_name] = latest
        else:
            print(f"[{os_name}] Version unchanged: {latest}")

    save_versions(updated_versions)


if __name__ == "__main__":
    while True:
        check_for_updates()
        time.sleep(CHECK_INTERVAL)


# Made By Avexy
