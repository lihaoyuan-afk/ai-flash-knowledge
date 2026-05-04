import os
import sys

import httpx


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")

    if not token or not webhook_url:
        print("请先设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_WEBHOOK_URL")
        sys.exit(1)

    response = httpx.post(
        f"https://api.telegram.org/bot{token}/setWebhook",
        json={"url": webhook_url},
        timeout=20,
    )
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
