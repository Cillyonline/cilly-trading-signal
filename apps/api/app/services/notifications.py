import json
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings

TELEGRAM_API_BASE_URL = "https://api.telegram.org"
TELEGRAM_TEST_MESSAGE = "Cilly Trading Signal Telegram test message."

TelegramPost = Callable[[str, dict[str, object]], dict[str, Any]]


class TelegramConfigurationError(Exception):
    pass


class TelegramDeliveryError(Exception):
    pass


def send_telegram_test_message(http_post: TelegramPost | None = None) -> None:
    send_telegram_message(TELEGRAM_TEST_MESSAGE, http_post=http_post)


def send_telegram_message(message: str, http_post: TelegramPost | None = None) -> None:
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    if not token or not chat_id:
        raise TelegramConfigurationError

    post = http_post or _post_telegram_json
    response = post(
        f"{TELEGRAM_API_BASE_URL}/bot{token}/sendMessage",
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": True,
        },
    )
    if response.get("ok") is not True:
        raise TelegramDeliveryError


def _post_telegram_json(url: str, payload: dict[str, object]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as error:
        raise TelegramDeliveryError from error

    return json.loads(response_body)
