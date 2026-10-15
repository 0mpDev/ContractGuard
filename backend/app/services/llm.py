from functools import lru_cache

from groq import Groq

from app.config import GROQ_API_KEY


@lru_cache(maxsize=1)
def get_client() -> Groq:
    """Create the Groq client lazily so the app can boot (and /model-health can
    report a missing key) even when GROQ_API_KEY isn't configured yet."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to backend/.env or your host's environment variables."
        )
    return Groq(api_key=GROQ_API_KEY)
