from pydantic import BaseModel, EmailStr, Field, ConfigDict

class AuthInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

class SignupInput(AuthInput):
    allow_ai_training: bool = False

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    ai_training_consent: bool

class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
