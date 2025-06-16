FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl gnupg ca-certificates cron && \
    curl -fsSL https://packagecloud.io/ookla/speedtest-cli/gpgkey | gpg --dearmor -o /etc/apt/trusted.gpg.d/ookla-speedtest.gpg && \
    echo "deb https://packagecloud.io/ookla/speedtest-cli/debian/ bullseye main" > /etc/apt/sources.list.d/ookla_speedtest.list && \
    apt-get update && apt-get install -y speedtest && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY post_speedtest.py entrypoint.sh crontab.txt ./
RUN pip install requests
RUN chmod +x entrypoint.sh && crontab crontab.txt

ENTRYPOINT ["/app/entrypoint.sh"]
