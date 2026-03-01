import httpx
import random

BASE_URL = "https://api.heygen.com"


class HeyGenService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        }
        self._avatars_cache: list[dict] | None = None
        self._voices_cache: list[dict] | None = None

    async def list_avatars(self, force_refresh: bool = False) -> list[dict]:
        """Fetch streaming-compatible avatars from HeyGen. Results are cached."""
        if self._avatars_cache and not force_refresh:
            return self._avatars_cache

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/v1/streaming/avatar.list",
                headers=self.headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()

        raw = data.get("data", [])
        # data may be a list of avatars directly, or a dict with an "avatars" key
        avatars = raw.get("avatars", []) if isinstance(raw, dict) else raw
        # Filter to non-premium avatars only
        self._avatars_cache = [a for a in avatars if not a.get("premium", False)]
        return self._avatars_cache

    async def list_voices(self, force_refresh: bool = False) -> list[dict]:
        """Fetch available voices from HeyGen. Results are cached."""
        if self._voices_cache and not force_refresh:
            return self._voices_cache

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/v2/voices",
                headers=self.headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()

        self._voices_cache = data.get("data", {}).get("voices", [])
        return self._voices_cache

    def pick_random_avatars(self, avatars: list[dict], count: int) -> list[dict]:
        """Pick `count` random unique avatars from the list."""
        if count > len(avatars):
            # Allow duplicates if we need more than available
            return random.choices(avatars, k=count)
        return random.sample(avatars, k=count)

    def get_default_voice_id(self, avatar: dict, voices: list[dict]) -> str:
        """Get the default voice for an avatar, or fall back to a random voice."""
        default = avatar.get("default_voice_id")
        if default:
            return default
        # Fallback: pick a voice matching avatar gender
        gender = avatar.get("gender", "").lower()
        matching = [v for v in voices if v.get("gender", "").lower() == gender]
        if matching:
            return random.choice(matching)["voice_id"]
        if voices:
            return voices[0]["voice_id"]
        raise ValueError("No voices available")

    async def create_streaming_token(self) -> str:
        """Create a short-lived streaming token for the HeyGen Streaming Avatar SDK."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{BASE_URL}/v1/streaming.create_token",
                headers=self.headers,
                json={},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()

        token = data.get("data", {}).get("token")
        if not token:
            raise ValueError(f"Failed to create streaming token: {data}")
        return token
