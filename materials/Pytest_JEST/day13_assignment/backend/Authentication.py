import jwt
import bcrypt
import time

SECRET_KEY = "ShigeoYamazaki"
ALGO = "HS256"

users = {}

def signup(username: str, password: str, role: str):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users[username] = {"password_hash": password_hash, "role": role}
    print("successfully!")
    print(f"UserName : '{username}'\n Hash : {password_hash.decode()} \n Role : {role} \n")

def login(username: str, password:str) -> str | None:
    user = users.get(username)
    if not user:
        print(f"Login failed user: '{username}' not found. \n")
        return None

    if not bcrypt.checkpw(password.encode(), user["password_hash"]):
        print(f"Login failed user: wrong password \n")
        return None

    payload = {
        "sub": username,
        "role": user["role"],
        "exp": int(time.time()) + 60
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

    print(f"Login successful for '{username}'! Token issues. \n")
    return token

def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired \n")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token \n")
        return None

def require_role(token: str, allowed_roles: list[str]) -> dict | None:
    payload = decode_token(token)
    if payload["role"] in allowed_roles:
        print(f"Access granted. \n'{payload['sub']}' (role: {payload['role']}) \n")
        return payload

def delete_user(token: str, username_to_delete: str):
    payload = require_role(token, ["admin"])
    if payload:
        print(f"User {username_to_delete} deleted \n")
    else:
        print("Forbidden \n")

def view_profile(token: str):
    payload = require_role(token, ["admin", "user"])
    if payload:
        print(f"Showing profile for {payload['sub']} \n")
    else:
        print("Forbidden \n")
    
