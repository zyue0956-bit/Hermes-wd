"""Group name extraction and rate limiting for Feishu group chats."""
from __future__ import annotations

import re
import time

_GROUP_NAME_RE = re.compile(r"<group-name>([\s\S]*?)</group-name>")
_MAX_GROUP_NAME_LEN = 20


def extract_group_name(text: str) -> tuple[str, str | None]:
    match = _GROUP_NAME_RE.search(text)
    if not match:
        return text, None
    raw_name = match.group(1).strip()
    clean_text = _GROUP_NAME_RE.sub("", text).strip()
    if not raw_name:
        return clean_text, None
    return clean_text, raw_name[:_MAX_GROUP_NAME_LEN]


class GroupNameRateLimiter:
    def __init__(self, interval_seconds: int = 300):
        self._interval = interval_seconds
        self._last_update: dict[str, float] = {}

    def should_update(self, chat_id: str) -> bool:
        last = self._last_update.get(chat_id)
        if last is None:
            return True
        return (time.monotonic() - last) >= self._interval

    def record_update(self, chat_id: str) -> None:
        self._last_update[chat_id] = time.monotonic()
