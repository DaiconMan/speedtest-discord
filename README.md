# 📡 Speedtest Discord Reporter

Speedtest.net（Ookla公式CLI）を使って、定期的にインターネット速度を測定し、結果を **DiscordのWebhookにEmbed形式で自動投稿** するDocker Swarmサービスです。

---

## ✨ 機能

- Ookla公式CLIによる信頼性の高いスピード測定
- Discord Webhookに **見やすいEmbed形式** で自動投稿
- 測定結果に国旗、Pingの品質分類（🟢🟡🔴）、前回との差分を表示
- 1時間ごとに自動実行（cron）
- GitHub Actionsでの自動ビルド & GHCR公開
- Webhook URLはDocker Secretで安全に管理

---

## 📷 投稿イメージ（Discord上）

```
📡 Speedtest.net Result
ISP: NTT Communications
Server: 🇯🇵 Tokyo (Japan)
Download: 300.25 Mbps (+5.23)
Upload: 145.62 Mbps (-3.12)
Ping: 🟢 15.2 ms (Low)
```

---

## 🚀 クイックスタート（Docker Swarm）

### 🔸 前提条件

- Docker Swarm 初期化済み（`docker swarm init`）
- DiscordのWebhook URLを保持していること
- GHCRからPull可能なネットワーク接続

---

### ① Webhook URLをDocker Secretとして登録

```bash
docker secret create discord_webhook_url - <<EOF
https://discord.com/api/webhooks/xxxxxxxxxxxx
EOF
```

---

### ② Dockerイメージを取得

```bash
docker pull ghcr.io/daiconman/speedtest-discord:latest
```

---

### ③ サービスをデプロイ

```bash
docker stack deploy -c docker-stack.yml speedtest
```

---

### ✅ 動作確認

```bash
docker service logs speedtest_speedtest --follow
```

---

### 🧪 即時テスト投稿（1時間待たず確認したいとき）

```bash
docker exec -it $(docker ps -qf name=speedtest_speedtest) python3 /app/post_speedtest.py
```

---

## 🛠 開発者向け

### 📦 自分でビルドしたい場合

```bash
docker build -t speedtest-discord .
docker run -e DISCORD_WEBHOOK_URL=... speedtest-discord
```

---

### 🤖 GitHub Actions + GHCR

このリポジトリはGitHub Actionsを使用して、`ghcr.io/<your-name>/speedtest-discord:latest` に自動でイメージをPushします。

---

## 🔐 セキュリティについて

- Discord Webhookは外部公開しないでください
- Webhook URLは必ず Docker Secret で管理しましょう
- `secrets/` フォルダは `.gitignore` に追加しておくと安全です

---

## 🧩 今後の改善予定（PR歓迎）

- SQLite や InfluxDB への記録
- 結果のグラフ画像を生成してDiscordに添付
- ダッシュボード連携（Grafana etc.）
- Pingや速度の異常時だけ通知する「しきい値通知」

---

## 📄 ライセンス

MIT License

---

## 🙌 Special Thanks

- [Ookla CLI](https://www.speedtest.net/apps/cli)
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook)
