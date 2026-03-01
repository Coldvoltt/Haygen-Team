import httpx
import random

BASE_URL = "https://api.heygen.com"
UPLOAD_URL = "https://upload.heygen.com"


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
        """Fetch available avatars from HeyGen. Results are cached."""
        if self._avatars_cache and not force_refresh:
            return self._avatars_cache

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/v2/avatars",
                headers=self.headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()

        avatars = data.get("data", {}).get("avatars", [])
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
        if count <= 0:
            return []
        if count > len(avatars):
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

    async def upload_talking_photo(self, image_bytes: bytes, content_type: str) -> dict:
        """Upload an image to HeyGen as a talking photo.

        Returns dict with 'talking_photo_id' and 'talking_photo_url'.
        """
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": content_type,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{UPLOAD_URL}/v1/talking_photo",
                headers=headers,
                content=image_bytes,
                timeout=60.0,
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("code") != 100:
            raise ValueError(f"Talking photo upload failed: {data}")

        return data["data"]

    async def generate_video(
        self,
        voice_id: str,
        input_text: str,
        title: str = "Team Intro",
        avatar_id: str | None = None,
        talking_photo_id: str | None = None,
    ) -> str:
        """Create a video. Supply either avatar_id OR talking_photo_id."""
        if talking_photo_id:
            character = {
                "type": "talking_photo",
                "talking_photo_id": talking_photo_id,
                "talking_photo_style": "square",
                "talking_style": "stable",
            }
        elif avatar_id:
            character = {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": "normal",
            }
        else:
            raise ValueError("Must provide either avatar_id or talking_photo_id")

        payload = {
            "video_inputs": [
                {
                    "character": character,
                    "voice": {
                        "type": "text",
                        "voice_id": voice_id,
                        "input_text": input_text,
                        "speed": 1.0,
                    },
                    "background": {
                        "type": "color",
                        "value": "#FFFFFF",
                    },
                }
            ],
            "title": title,
            "dimension": {"width": 1280, "height": 720},
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{BASE_URL}/v2/video/generate",
                headers=self.headers,
                json=payload,
                timeout=60.0,
            )
            resp.raise_for_status()
            data = resp.json()

        video_id = data.get("data", {}).get("video_id")
        if not video_id:
            raise ValueError(f"Failed to create video: {data}")
        return video_id

    async def get_video_status(self, video_id: str) -> dict:
        """Check the status of a video. Returns dict with status, video_url, etc."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/v1/video_status.get",
                headers=self.headers,
                params={"video_id": video_id},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()

        return data.get("data", {})
