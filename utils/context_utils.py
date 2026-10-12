from typing import Dict
import tiktoken


def _encoding():
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def count_tokens(text: str) -> int:
    if not text:
        return 0
    enc = _encoding()
    if enc is None:
        return max(1, len(text) // 4)
    return len(enc.encode(text))


def truncate_to_tokens(text: str, token_budget: int) -> str:
    if token_budget <= 0:
        return ""
    enc = _encoding()
    if enc is None:
        return text[: token_budget * 4]
    tokens = enc.encode(text)
    if len(tokens) <= token_budget:
        return text
    return enc.decode(tokens[:token_budget])


def analyze_context(text: str, system_prompt: str, context_limit: int,
                    reserved_output_tokens: int, safety_margin: int) -> Dict:
    input_tokens = count_tokens(text)
    system_tokens = count_tokens(system_prompt)
    available_input_budget = max(
        0,
        context_limit - reserved_output_tokens - safety_margin - system_tokens,
    )
    overflow_tokens = max(0, input_tokens - available_input_budget)

    if overflow_tokens > 0:
        status = "OVERFLOW"
    elif available_input_budget and input_tokens >= available_input_budget * 0.85:
        status = "WARNING"
    else:
        status = "SAFE"

    return {
        "input_tokens": input_tokens,
        "system_tokens": system_tokens,
        "available_input_budget": available_input_budget,
        "overflow_tokens": overflow_tokens,
        "status": status,
    }
