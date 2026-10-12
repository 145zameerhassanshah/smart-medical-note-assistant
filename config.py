import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Smart Medical Note Assistant"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openrouter/free").strip()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

REQUEST_TIMEOUT = 45
MAX_RETRIES = 3
BASE_DELAY = 1.0

DEFAULT_CONTEXT_LIMIT = 8192
RESERVED_OUTPUT_TOKENS = 1200
SAFETY_MARGIN = 256


def validate_config():
    errors = []
    if not OPENROUTER_API_KEY:
        errors.append("OPENROUTER_API_KEY is missing.")
    if not DEFAULT_MODEL:
        errors.append("DEFAULT_MODEL is missing.")
    return errors
