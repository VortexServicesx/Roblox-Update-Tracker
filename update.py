# Made By Avexy

# imports
import requests
import time
import os

# configs
WEBHOOK_URL = ""  # replace with your webhook
VERSION_FILE = "roblox_version.txt"
CHECK_INTERVAL = 120

# urls
CLIENT_SETTINGS = "https://clientsettings.roblox.com/v2/client-version/"

# binaries
BINARY_TYPES = {
    "Windows": "WindowsPlayer",
    "Mac": "MacPlayer"
}

# beta channels
BETA_CHANNELS = {
    "Windows Beta": ("WindowsPlayer", "ZBeta"),
    "Mac Beta": ("MacPlayer", "ZBeta")
}


# fetch version
def fetch_latest_version(binary_type: str, channel: str = None) -> str:
    if channel:
        url = f"{CLIENT_SETTINGS}{binary_type}/channel/{channel}"
    else:
        url = f"{CLIENT_SETTINGS}{binary_type}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    version = data.get("clientVersionUpload")

    if not version:
        raise ValueError(f"No version found for {binary_type}")

    return version


# load saved versions
def load_saved_versions() -> dict:
    if not os.path.exists(VERSION_FILE):
        return {}

    with open(VERSION_FILE, "r") as f:
        lines = f.read().strip().splitlines()

    versions = {}

    for line in lines:
        if "=" in line:
            name, version = line.split("=", 1)
            versions[name.strip()] = version.strip()

    return versions


# save versions
def save_versions(versions: dict):
    with open(VERSION_FILE, "w") as f:
        for name, version in versions.items():
            f.write(f"{name}={version}\n")


# normal update webhook
def send_discord_update(os_name: str, old: str, new: str):
    embed = {
        "title": f"Roblox {os_name} Updated",
        "color": 0x5E095E,
        "fields": [
            {
                "name": "Old Version",
                "value": f"`{old}`",
                "inline": True
            },
            {
                "name": "New Version",
                "value": f"`{new}`",
                "inline": True
            }
        ]
    }

    requests.post(
        WEBHOOK_URL,
        json={"embeds": [embed]}
    ).raise_for_status()


# beta/future update webhook
def send_discord_future_update(os_name: str, old: str, new: str):
    embed = {
        "title": f"Future Roblox {os_name} Update Detected",
        "description": "A new version was detected!.",
        "color": 0x8A2BE2,
        "fields": [
            {
                "name": "Old Beta Version",
                "value": f"`{old}`",
                "inline": True
            },
            {
                "name": "New Beta Version",
                "value": f"`{new}`",
                "inline": True
            }
        ]
    }

    requests.post(
        WEBHOOK_URL,
        json={"embeds": [embed]}
    ).raise_for_status()


# update checker
def check_for_updates():
    saved_versions = load_saved_versions()
    updated_versions = saved_versions.copy()

    # normal versions
    for os_name, binary in BINARY_TYPES.items():
        try:
            latest = fetch_latest_version(binary)
        except Exception as e:
            print(f"[ERROR] {os_name}: {e}")
            continue

        old = saved_versions.get(os_name)

        if old is None:
            print(f"[{os_name}] Saving initial version: {latest}")
            updated_versions[os_name] = latest

        elif latest != old:
            print(f"[{os_name}] Updated: {old} -> {latest}")
            send_discord_update(os_name, old, latest)
            updated_versions[os_name] = latest

        else:
            print(f"[{os_name}] No changes.")

    # beta versions
    for beta_name, (binary, channel) in BETA_CHANNELS.items():
        try:
            latest_beta = fetch_latest_version(binary, channel)
        except Exception as e:
            print(f"[ERROR] {beta_name}: {e}")
            continue

        old_beta = saved_versions.get(beta_name)

        if old_beta is None:
            print(f"[{beta_name}] Saving initial beta version: {latest_beta}")
            updated_versions[beta_name] = latest_beta

        elif latest_beta != old_beta:
            print(f"[{beta_name}] Future update detected!")
            print(f"{old_beta} -> {latest_beta}")

            send_discord_future_update(
                beta_name,
                old_beta,
                latest_beta
            )

            updated_versions[beta_name] = latest_beta

        else:
            print(f"[{beta_name}] No beta changes.")

    save_versions(updated_versions)


# main loop
if __name__ == "__main__":
    while True:
        check_for_updates()
        time.sleep(CHECK_INTERVAL)


# Made By Avexy
