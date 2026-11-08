from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.services.script_generator import ScriptRequest, generate_script

router = APIRouter(prefix="/api/scripts", tags=["scripts"])
bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Please log in to create an advert.")
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        user_id = int(payload.get("sub", ""))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Your session has expired. Please log in again.")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Your account could not be found. Please log in again.")
    return user


@router.post("/generate")
def create_script(payload: ScriptRequest, _user: User = Depends(current_user)):
    try:
        script, generation_mode = generate_script(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"script": script.model_dump(), "generation_mode": generation_mode}
