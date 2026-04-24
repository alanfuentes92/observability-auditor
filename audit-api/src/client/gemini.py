import asyncio
import logging

from google import genai
from google.genai import errors

log = logging.getLogger(__name__)

FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]


class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", rate_limit_delay: float = 5.0):
        self._client = genai.Client(api_key=api_key)
        self.model = model
        self._rate_limit_delay = rate_limit_delay
        self._last_request_time: float = 0

    async def generate(self, prompt: str) -> str:
        # Rate limiting: space requests to avoid quota burn
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._rate_limit_delay and self._last_request_time > 0:
            await asyncio.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        last_error = None

        for model in models_to_try:
            for attempt in range(3):
                try:
                    response = self._client.models.generate_content(
                        model=model, contents=prompt,
                    )
                    text = response.text or ""
                    if not text and response.candidates:
                        # Try to extract from candidates
                        for c in response.candidates:
                            if c.content and c.content.parts:
                                text = c.content.parts[0].text or ""
                                if text:
                                    break
                    if model != self.model:
                        log.info(f"Used fallback model: {model}")
                    return text if text else "*Análisis no disponible — respuesta vacía del modelo.*"
                except errors.ServerError as e:
                    last_error = e
                    wait = (2 ** attempt) + 1
                    log.warning(f"Gemini {model} attempt {attempt+1}/3 failed (503), retrying in {wait}s...")
                    await asyncio.sleep(wait)
                except errors.ClientError as e:
                    last_error = e
                    # 429 = quota exhausted — respect retryDelay if present
                    status = getattr(e, 'status', 0)
                    if status == 429 and attempt < 2:
                        # Try to extract retry delay from error message
                        import re
                        match = re.search(r'retry in ([\d.]+)s', str(e))
                        wait = min(float(match.group(1)), 60) if match else (2 ** attempt) + 1
                        log.warning(f"Gemini {model} rate limited, waiting {wait:.0f}s...")
                        await asyncio.sleep(wait)
                        continue
                    log.warning(f"Gemini {model} client error: {e}, trying next model...")
                    break

        log.error(f"All Gemini models failed. Last error: {last_error}")
        return "*Análisis no disponible — el servicio de IA no respondió. Reintente más tarde.*"
