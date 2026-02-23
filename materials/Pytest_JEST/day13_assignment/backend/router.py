from fastapi import APIRouter, HTTPException, Depends, Header
from .models import UserRegister, UserLogin, UserProfile
from .Authentication import signup, login, decode_token, users

router = APIRouter()

@router.post("/login")
def login_user(user: UserLogin):
    token = login(user.username, user.password)
    if not token:
        raise HTTPException(status_code=400, detail="token has not generated")
    
    return {"access_token": token, "token_type":"bearer"}

@router.post("/register")
def create_user(user: UserRegister):
    if user.username in users:
        raise HTTPException(status_code=400, detail="Error Code =400: This User is already registered.")
    signup(user.username, user.password, user.role)
    
    return {"message": "User registered successfully"}

@router.get("/profile")
def get_profile(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"username": payload["sub"], "role": payload["role"]}