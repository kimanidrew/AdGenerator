"""Hosted OpenAI-compatible image generation provider for scene storyboards."""
from __future__ import annotations

import base64
import binascii
import re
from urllib.parse import urlsplit
from uuid import uuid4

import httpx

from app.config import settings


def _safe_segment(value: str) -> str:
    return (re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-") or "advert")[:48]


def _scene_prompt(script, scene) -> str:
    return (
        "Create one photorealistic vertical 9:16 storyboard frame for a premium Kenyan social-media advert. "
        "Use believable Kenyan people, locations and details. One image only: no collage, panels, subtitles, "
        "logos or watermarks. Do not render written text; text will be overlaid separately. "
        f"Product: {script.product_name}. Audience: {script.target_audience}. Tone: {script.tone}. "
        f"Scene {scene.scene_number} of {len(script.scenes)}. Visual direction: {scene.visual_direction}. "
        "Keep the product clearly visible and its appearance consistent."
    )


async def generate_scene_image(script, scene) -> tuple[bytes, str]:
    base_url = (settings.image_generation_base_url or "").strip().rstrip("/")
    if not base_url:
        raise RuntimeError(
            "Image generation is not configured. Add IMAGE_GENERATION_BASE_URL and "
            "IMAGE_GENERATION_MODEL for your hosted GPU image endpoint."
        )
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise RuntimeError("IMAGE_GENERATION_BASE_URL must use HTTPS.")
    endpoint = base_url if base_url.endswith("/images/generations") else base_url + "/images/generations"
    headers = {"Content-Type": "application/json"}
    if settings.image_generation_api_key:
        headers["Authorization"] = f"Bearer {settings.image_generation_api_key}"
    payload = {
        "model": settings.image_generation_model,
        "prompt": _scene_prompt(script, scene),
        "size": "1024x1792",
        "n": 1,
        "response_format": "b64_json",
    }
    timeout = httpx.Timeout(settings.image_generation_timeout_seconds, connect=20.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(endpoint, headers=headers, json=payload)
    if response.status_code >= 400:
        raise RuntimeError(f"Image provider returned HTTP {response.status_code}: {response.text[:400]}")
    try:
        encoded = response.json()["data"][0]["b64_json"]
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, KeyError, IndexError, TypeError, binascii.Error) as exc:
        raise RuntimeError("Image provider must return data[0].b64_json.") from exc
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("Image provider must return PNG image data.")
    if len(image_bytes) > 15 * 1024 * 1024:
        raise RuntimeError("Generated image exceeds the 15 MB scene-image limit.")
    return image_bytes, _scene_prompt(script, scene)


async def generate_storyboard(script, user_id: int):
    from app.storage import create_download_url, upload_bytes

    results = []
    batch_id = uuid4().hex
    brand = _safe_segment(script.product_name)
    for scene in script.scenes:
        image_bytes, prompt = await generate_scene_image(script, scene)
        key = f"storyboards/user-{user_id}/{brand}/{batch_id}/scene-{scene.scene_number}.png"
        upload_bytes(key, image_bytes, "image/png")
        results.append({
            "scene_number": scene.scene_number,
            "image_url": create_download_url(key, expires_in=900),
            "prompt": prompt,
        })
    return results
