import asyncio

from app.services.image_generator import generate_storyboard
from app.services.script_generator import GeneratedScript
from app.worker.celery_app import celery_app


@celery_app.task(bind=True, name="kenyaads.generate_storyboard")
def generate_storyboard_task(self, script_data: dict, user_id: int):
    script = GeneratedScript.model_validate(script_data)
    self.update_state(
        state="PROGRESS",
        meta={"user_id": user_id, "completed_scenes": 0, "total_scenes": len(script.scenes)},
    )
    images = asyncio.run(generate_storyboard(script, user_id))
    return {"user_id": user_id, "images": images}
