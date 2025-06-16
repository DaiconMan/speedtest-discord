import subprocess, json, requests

def get_webhook_url():
    with open("/run/secrets/discord_webhook_url", "r") as f:
        return f.read().strip()

def run_speedtest():
    result = subprocess.run(
        ["/usr/bin/speedtest", "--accept-license", "--accept-gdpr", "-f", "json"],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(result.stderr)
    return json.loads(result.stdout)

def format_result(data):
    download = data["download"]["bandwidth"] * 8 / 1_000_000
    upload = data["upload"]["bandwidth"] * 8 / 1_000_000
    ping = data["ping"]["latency"]
    isp = data["isp"]
    server = data["server"]["name"]
    return f"""📡 **Speedtest.net Result**
- ISP: {isp}
- Server: {server}
- Download: {download:.2f} Mbps
- Upload: {upload:.2f} Mbps
- Ping: {ping:.2f} ms
"""

def post_to_discord(message, url):
    requests.post(url, json={"content": message})

if __name__ == "__main__":
    try:
        url = get_webhook_url()
        result = run_speedtest()
        message = format_result(result)
        post_to_discord(message, url)
    except Exception as e:
        post_to_discord(f"❗ Speedtest failed:\n```\n{str(e)}\n```", get_webhook_url())
