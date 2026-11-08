from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.routes.scripts import current_user
from app.services.image_generator import generate_storyboard
from app.services.script_generator import GeneratedScript

router = APIRouter(prefix="/api/storyboards", tags=["storyboards"])


class StoryboardRequest(BaseModel):
    script: GeneratedScript


@router.post("/generate")
async def create_storyboard(payload: StoryboardRequest, user=Depends(current_user)):
    try:
        images = await generate_storyboard(payload.script, user.id)
    except RuntimeError as exc:
        message = str(exc)
        status = 503 if "not configured" in message.lower() else 502
        raise HTTPException(status_code=status, detail=message) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Storyboard generation failed. Check your image provider and R2 configuration.",
        ) from exc
    return {"images": images, "image_count": len(images)}
