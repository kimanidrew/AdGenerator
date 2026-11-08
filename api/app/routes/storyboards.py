from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.routes.scripts import current_user
from app.services.script_generator import GeneratedScript
from app.worker.celery_app import celery_app

router = APIRouter(prefix="/api/storyboards", tags=["storyboards"])


class StoryboardRequest(BaseModel):
    script: GeneratedScript


@router.post("/generate", status_code=202)
def create_storyboard(payload: StoryboardRequest, user=Depends(current_user)):
    task = celery_app.send_task("kenyaads.generate_storyboard", args=[payload.script.model_dump(), user.id])
    return {"job_id": task.id, "status": "queued"}


@router.get("/jobs/{job_id}")
def storyboard_job_status(job_id: str, user=Depends(current_user)):
    result = AsyncResult(job_id, app=celery_app)
    state = result.state
    if state == "SUCCESS":
        data = result.result or {}
        if data.get("user_id") != user.id:
            raise HTTPException(status_code=404, detail="Storyboard job not found.")
        images = data.get("images", [])
        return {"status": "completed", "images": images, "image_count": len(images)}
    if state == "FAILURE":
        raise HTTPException(status_code=502, detail="Storyboard generation failed. Check the image provider and R2 configuration.")
    if state == "PROGRESS":
        meta = result.info if isinstance(result.info, dict) else {}
        if meta.get("user_id") != user.id:
            raise HTTPException(status_code=404, detail="Storyboard job not found.")
        return {"status": "processing", "completed_scenes": meta.get("completed_scenes", 0), "total_scenes": meta.get("total_scenes", 0)}
    return {"status": "queued"}
