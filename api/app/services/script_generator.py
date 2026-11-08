from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, Field, ValidationError, model_validator

from app.config import settings


class ScriptRequest(BaseModel):
    brief: str = Field(min_length=10, max_length=1200)
    product_name: str = Field(default="Your product", min_length=1, max_length=100)
    industry: str = Field(default="General", max_length=80)
    audience: str = Field(default="Everyday Kenyan consumers", max_length=160)
    language: str = Field(default="English", pattern="^(English|Kiswahili|Sheng)$")
    duration_seconds: int = Field(default=15, ge=10, le=60)
    platform: str = Field(default="TikTok", pattern="^(TikTok|Instagram Reels|YouTube Shorts|Facebook)$")
    tone: str = Field(default="Energetic", pattern="^(Energetic|Funny|Premium|Friendly|Inspirational|Trustworthy)$")


class ScriptScene(BaseModel):
    scene_number: int = Field(ge=1, le=8)
    duration_seconds: int = Field(ge=1, le=20)
    visual_direction: str = Field(min_length=5, max_length=400)
    voiceover: str = Field(min_length=2, max_length=500)
    on_screen_text: str = Field(max_length=120)
    transition: str = Field(default="Cut", max_length=80)


class GeneratedScript(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    product_name: str = Field(min_length=1, max_length=100)
    language: str
    duration_seconds: int
    platform: str
    tone: str
    target_audience: str
    scenes: list[ScriptScene] = Field(min_length=3, max_length=8)
    caption: str = Field(min_length=2, max_length=500)
    hashtags: list[str] = Field(min_length=2, max_length=12)
    call_to_action: str = Field(min_length=2, max_length=160)

    @model_validator(mode="after")
    def validate_scene_timing(self):
        if sum(scene.duration_seconds for scene in self.scenes) != self.duration_seconds:
            raise ValueError("Scene durations must add up to the requested ad duration.")
        if [scene.scene_number for scene in self.scenes] != list(range(1, len(self.scenes) + 1)):
            raise ValueError("Scene numbers must be consecutive and start at 1.")
        return self


def _starter_script(request: ScriptRequest) -> GeneratedScript:
    duration = request.duration_seconds
    scene_count = 4 if duration <= 30 else 5
    base, remainder = divmod(duration, scene_count)
    timings = [base + (1 if i < remainder else 0) for i in range(scene_count)]

    words = {
        "English": {
            "hook": f"Looking for something better? Meet {request.product_name}.",
            "benefit": "Made to fit your day and make every moment count.",
            "proof": "Simple, reliable and ready when you are.",
            "offer": "Make the smart choice today.",
            "cta": "Get yours today. Send us a message to order.",
            "caption": f"Make your day better with {request.product_name}. Ready when you are.",
        },
        "Kiswahili": {
            "hook": f"Unatafuta kitu bora? Kutana na {request.product_name}.",
            "benefit": "Imetengenezwa kurahisisha siku yako na kukupa thamani.",
            "proof": "Rahisi kutumia, ya kuaminika na tayari kwa ajili yako.",
            "offer": "Chagua kilicho bora leo.",
            "cta": "Pata yako leo. Tutumie ujumbe kuagiza.",
            "caption": f"Fanya siku yako iwe bora na {request.product_name}.",
        },
        "Sheng": {
            "hook": f"Unataka kitu fiti? Check {request.product_name}!",
            "benefit": "Inaendana na hustle yako na vibe ya kila siku.",
            "proof": "Ni simple, reliable na iko ready.",
            "offer": "Usibaki nyuma, make your move leo.",
            "cta": "DM sasa hivi upate yako!",
            "caption": f"Level up your day na {request.product_name}. Uko ready?",
        },
    }[request.language]

    beats = [
        ("Open with a relatable Kenyan everyday moment. Show the problem or desire clearly.", words["hook"], request.product_name.upper()),
        ("Reveal the product in a clean, well-lit hero shot. Show one clear benefit.", words["benefit"], "MADE FOR YOUR DAY"),
        ("Show the product being used in a believable setting relevant to the audience.", words["proof"], "QUALITY YOU CAN TRUST"),
        ("Finish with a confident product shot and a clear next step for the viewer.", words["offer"] + " " + words["cta"], "GET YOURS TODAY"),
    ]
    if scene_count == 5:
        beats.insert(3, ("Show a close-up detail or a happy customer moment. Keep the product in focus.", words["proof"], "THE DIFFERENCE IS IN THE DETAILS"))

    scenes = [
        ScriptScene(
            scene_number=index + 1,
            duration_seconds=timings[index],
            visual_direction=visual,
            voiceover=voice,
            on_screen_text=screen,
            transition="Quick cut" if index < scene_count - 1 else "End card",
        )
        for index, (visual, voice, screen) in enumerate(beats)
    ]
    return GeneratedScript(
        title=f"{request.product_name} — {request.tone} {request.duration_seconds}s advert",
        product_name=request.product_name,
        language=request.language,
        duration_seconds=duration,
        platform=request.platform,
        tone=request.tone,
        target_audience=request.audience,
        scenes=scenes,
        caption=words["caption"],
        hashtags=["KenyaAdsAI", "MadeInKenya", request.industry.replace(" ", "")],
        call_to_action=words["cta"],
    )


def _extract_json(content: str) -> str:
    cleaned = content.strip()
    cleaned = re.sub(r"^\x60{3}(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*\x60{3}$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The model did not return a JSON object.")
    return cleaned[start : end + 1]


def _self_hosted_script(request: ScriptRequest) -> GeneratedScript:
    endpoint = settings.script_llm_base_url.rstrip("/") + "/chat/completions"
    system_prompt = (
        "You are KenyaAds AI, an expert short-form advertising scriptwriter for Kenya. "
        "Create culturally grounded, respectful adverts. Do not invent product certifications, "
        "prices, guarantees or factual claims. Return only valid JSON matching the requested schema. "
        "The scenes array must contain 3 to 8 scenes; integer scene durations must sum exactly "
        "to duration_seconds. Use the requested language naturally. Do not imitate a real person's voice."
    )
    user_prompt = {
        "task": "Create a concise, shootable vertical video advert script.",
        "brief": request.brief,
        "product_name": request.product_name,
        "industry": request.industry,
        "audience": request.audience,
        "language": request.language,
        "duration_seconds": request.duration_seconds,
        "platform": request.platform,
        "tone": request.tone,
        "required_json": {
            "title": "string",
            "product_name": "string",
            "language": "string",
            "duration_seconds": "integer",
            "platform": "string",
            "tone": "string",
            "target_audience": "string",
            "scenes": [{
                "scene_number": "integer starting at 1",
                "duration_seconds": "integer",
                "visual_direction": "specific visual action and Kenyan setting",
                "voiceover": "spoken line",
                "on_screen_text": "short readable overlay",
                "transition": "short transition direction"
            }],
            "caption": "social caption",
            "hashtags": ["hashtag strings"],
            "call_to_action": "clear next step"
        }
    }
    body = json.dumps({
        "model": settings.script_llm_model,
        "temperature": 0.7,
        "max_tokens": 2500,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
        ],
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if settings.script_llm_api_key:
        headers["Authorization"] = f"Bearer {settings.script_llm_api_key}"
    req = Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=settings.script_llm_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        return GeneratedScript.model_validate_json(_extract_json(content))
    except HTTPError as exc:
        raise RuntimeError(f"Self-hosted model returned HTTP {exc.code}.") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Could not reach the configured script model. Check its URL and availability.") from exc
    except (KeyError, IndexError, TypeError, ValueError, ValidationError) as exc:
        raise RuntimeError("The configured model returned a response that did not match the script schema.") from exc


def generate_script(request: ScriptRequest) -> tuple[GeneratedScript, str]:
    if settings.script_llm_base_url:
        script = _self_hosted_script(request)
        mode = "self_hosted_llm"
    else:
        script = _starter_script(request)
        mode = "starter_template"

    # Keep the output aligned with the user's selected settings, even if a model drifts.
    if (
        script.duration_seconds != request.duration_seconds
        or script.language != request.language
        or script.platform != request.platform
        or script.tone != request.tone
    ):
        raise RuntimeError("The generated script did not preserve your selected language, duration, platform and tone. Please try again.")
    return script, mode
