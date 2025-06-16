import subprocess, json, requests, datetime, os

WEBHOOK_SECRET_PATH = "/run/secrets/discord_webhook_url"
CACHE_FILE = "/app/last_result.json"

# 絵文字付きPing評価
def ping_quality(ping):
    if ping < 30:
        return f"🟢 {ping:.1f} ms (Low)"
    elif ping < 70:
        return f"🟡 {ping:.1f} ms (Moderate)"
    else:
        return f"🔴 {ping:.1f} ms (High)"

# 国コードを国旗に変換
def country_flag(country_code):
    if not country_code:
        return "🌐"
    return ''.join([chr(0x1F1E6 + ord(c.upper()) - ord('A')) for c in country_code[:2]])

# 前回の測定結果を読み込む
def load_last_result():
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

# 今回の測定結果を保存する
def save_current_result(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

def get_webhook_url():
    with open(WEBHOOK_SECRET_PATH, "r") as f:
        return f.read().strip()

def run_speedtest():
    result = subprocess.run(
        ["/usr/bin/speedtest", "--accept-license", "--accept-gdpr", "-f", "json"],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(result.stderr)
    return json.loads(result.stdout)

def format_embed(data, previous):
    download = data["download"]["bandwidth"] * 8 / 1_000_000
    upload = data["upload"]["bandwidth"] * 8 / 1_000_000
    ping = data["ping"]["latency"]
    isp = data["isp"]
    server = data["server"]["name"]
    country = data["server"].get("country", "")
    flag = country_flag(data["server"].get("countryCode", ""))

    # 差分表示
    def diff(current, prev, unit=""):
        if prev is None:
            return f"{current:.2f}{unit} (N/A)"
        delta = current - prev
        sign = "🟢 +{:.2f}" if delta > 0 else "🔴 {:+.2f}"
        return f"{current:.2f}{unit} ({sign.format(delta)})"

    previous_dl = previous.get("download") if previous else None
    previous_ul = previous.get("upload") if previous else None
    previous_ping = previous.get("ping") if previous else None

    timestamp = datetime.datetime.utcnow().isoformat()

    return {
        "embeds": [
            {
                "title": "📡 Speedtest.net Result",
                "color": 0x00BFFF,
                "fields": [
                    {"name": "ISP", "value": isp, "inline": True},
                    {"name": "Server", "value": f"{flag} {server} ({country})", "inline": True},
                    {"name": "Download", "value": diff(download, previous_dl, " Mbps"), "inline": True},
                    {"name": "Upload", "value": diff(upload, previous_ul, " Mbps"), "inline": True},
                    {"name": "Ping", "value": ping_quality(ping), "inline": True}
                ],
                "timestamp": timestamp
            }
        ]
    }

def format_error_embed(error):
    timestamp = datetime.datetime.utcnow().isoformat()
    return {
        "embeds": [
            {
                "title": "❌ Speedtest Failed",
                "description": f"```\n{error}\n```",
                "color": 0xFF0000,
                "timestamp": timestamp
            }
        ]
    }

def post_to_discord(payload, url):
    response = requests.post(url, json=payload)
    if response.status_code >= 400:
        print(f"Failed to send Discord webhook: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    try:
        url = get_webhook_url()
        result = run_speedtest()

        current_data = {
            "download": result["download"]["bandwidth"] * 8 / 1_000_000,
            "upload": result["upload"]["bandwidth"] * 8 / 1_000_000,
            "ping": result["ping"]["latency"]
        }

        previous = load_last_result()
        payload = format_embed(result, previous)
        post_to_discord(payload, url)
        save_current_result(current_data)

    except Exception as e:
        payload = format_error_embed(str(e))
        post_to_discord(payload, get_webhook_url())
