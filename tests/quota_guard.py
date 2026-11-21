"""Shared daily request quota guard for Reqres API calls across Pytest and Locust.

The cap is read from the REQRES_DAILY_LIMIT environment variable.
If that variable is not set, it defaults to 35 — a conservative margin below the
40-requests/day anonymous limit the API has actually enforced in practice.

The assignment states a limit of 100 calls/day. The Reqres API has returned:
  "You've hit the anonymous demo limit of 40 requests/day"
So 35 is the safe default. Set REQRES_DAILY_LIMIT=90 only if you have an API key.
"""

import json
import logging
import os
from datetime import date

import pytest

logger = logging.getLogger(__name__)

# Read cap from environment variable; fall back to 35 (safe margin below the
# 40/day limit the anonymous Reqres API has actually enforced).
DAILY_QUOTA_LIMIT = int(os.environ.get("REQRES_DAILY_LIMIT", "35"))

QUOTA_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "reports",
    ".reqres_quota.json",
)


def _load_quota() -> dict:
    """Load today's quota record from file, or return a fresh zero-count record."""
    today_str = date.today().isoformat()
    if os.path.exists(QUOTA_FILE_PATH):
        try:
            with open(QUOTA_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Only reuse the file if it is from today and has a valid count.
                if data.get("date") == today_str and isinstance(data.get("count"), int):
                    return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"date": today_str, "count": 0}


def _save_quota(data: dict) -> None:
    """Persist the quota record to reports/.reqres_quota.json."""
    os.makedirs(os.path.dirname(QUOTA_FILE_PATH), exist_ok=True)
    with open(QUOTA_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_current_quota_count() -> int:
    """Return the number of live API requests recorded today."""
    return _load_quota()["count"]


def check_and_increment_quota(limit: int = DAILY_QUOTA_LIMIT) -> bool:
    """
    Check whether today's count is under the limit.
    If so, increment by 1, persist, and return True (allowed).
    If the limit is already reached, return False (blocked).
    """
    data = _load_quota()
    if data["count"] >= limit:
        return False
    data["count"] += 1
    _save_quota(data)
    return True


def enforce_api_quota(api_base_url: str = "", limit: int = DAILY_QUOTA_LIMIT) -> None:
    """
    Skip the current test if the daily quota is exhausted.
    Calls against the local mock server (127.0.0.1 / localhost) are free — no quota consumed.
    """
    if "127.0.0.1" in api_base_url or "localhost" in api_base_url:
        return

    if not check_and_increment_quota(limit):
        pytest.skip(
            f"Daily Reqres API cap of {limit} calls reached "
            f"(today's recorded count is {get_current_quota_count()}). "
            "To raise the cap set REQRES_DAILY_LIMIT=<n> (requires an API key for >40)."
        )


# Log today's count every time this module is imported, so it is visible
# in Locust startup output and in pytest's captured log.
logger.info(
    "quota_guard loaded — today's recorded Reqres call count: %d / %d (cap)",
    get_current_quota_count(),
    DAILY_QUOTA_LIMIT,
)
