import jwt
import bcrypt
import time

SECRET_KEY = "YuichiYamazaki"
ALGO = "HS256"

# Step1 User "Database" + Signup
users = {}

def signup(username: str, password: str, role: str):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users[username] = {"password_hash": password_hash, "role": role}
    print("successfully!")
    print(f"UserName : '{username}'\n Hash : {password_hash.decode()} \n Role : {role} \n")

# Step2 – Login and JWT Issuance
def login(username: str, password: str) -> str | None:
    user = users.get(username)
    if not user:
        print(f"Login failed: user '{username}' not found. \n")
        return None
    if not bcrypt.checkpw(password.encode(), user["password_hash"]):
        print(f"Login failed: wrong password \n")
        return None
    payload = {
        "sub": username,
        "role": user["role"],
        "exp": int(time.time()) + 60
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

    print(f"Login successful for '{username}'! Token issued. \n")
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
    if payload is None:
        return None
    if payload["role"] in allowed_roles:
        print(f"Access granted. \n'{payload['sub']}' (role: {payload['role']}) \n")
        return payload
    else:
        print(f"Access denied \n'{payload['sub']}' (role: {payload['role']}) \n")
        return None

# Step4 – Fake Protected Endpoints

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

if __name__ == "__main__":
    # Step 1: Signup
    signup("alice", "123456", "admin")
    signup("bob", "12354", "user")
    print("All users:", list(users.keys()))

    # Step 2: Login and print tokens
    print("\nstep2\n")
    alice_token = login("alice", "123456")
    print(f"  Alice's token: {alice_token}")

    bob_token = login("bob", "12354")
    print(f"  Bob's token: {bob_token}")

    result = login("alice", "333333")
    print(f"  Result: {result}")
    
    # Step 3: Token Validation + Authorization
    decoded = decode_token(alice_token)
    print("--- Step3 ---")
    require_role(alice_token, ["admin"])
    require_role(bob_token, ["admin"])

    require_role(alice_token, ["admin", "user"])
    require_role(bob_token, ["admin", "user"])

    print("--- Invalid Token ---")
    require_role("bad token", ["admin"])

    print("--- Step4 ---")

    print("Alice tries delete_user:")
    delete_user(alice_token, "bob")

    print("Alice tries view_profile:")
    view_profile(alice_token)

    # Bob (user) — cannot delete, but can view profile
    print("Bob tries delete_user:")
    delete_user(bob_token, "alice")

    print("Bob tries view_profile:")
    view_profile(bob_token)

