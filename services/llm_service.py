import random
import time
from typing import Dict, Any
import requests

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_URL,
    DEFAULT_MODEL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    BASE_DELAY,
)

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _headers():
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }


def send_chat_request(system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> Dict[str, Any]:
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers=_headers(),
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        delay = float(retry_after)
                    except ValueError:
                        delay = BASE_DELAY * (2 ** (attempt - 1))
                else:
                    delay = BASE_DELAY * (2 ** (attempt - 1))

                delay += random.uniform(0, 0.5)
                time.sleep(delay)
                continue

            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")

            if not content:
                return {
                    "success": False,
                    "stage": "response_parsing",
                    "error": "The API returned no assistant content.",
                    "content": None,
                }

            return {
                "success": True,
                "stage": "complete",
                "error": None,
                "content": content,
                "raw_response": data,
            }

        except requests.Timeout as exc:
            last_error = f"Request timed out: {exc}"
        except requests.ConnectionError as exc:
            last_error = f"Network connection failed: {exc}"
        except requests.HTTPError as exc:
            status = getattr(exc.response, "status_code", None)
            return {
                "success": False,
                "stage": "http_error",
                "error": f"HTTP error {status}: {exc}",
                "content": None,
            }
        except requests.RequestException as exc:
            last_error = f"Request failed: {exc}"
        except ValueError as exc:
            return {
                "success": False,
                "stage": "response_parsing",
                "error": f"Invalid API response: {exc}",
                "content": None,
            }

        if attempt < MAX_RETRIES:
            delay = BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            time.sleep(delay)

    return {
        "success": False,
        "stage": "network",
        "error": last_error or "Request failed after retry attempts.",
        "content": None,
    }
