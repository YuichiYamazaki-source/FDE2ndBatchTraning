from fastapi.testclient import TestClient
from backend.main import app
from backend.Authentication import users

client = TestClient(app)

test_user ={
    "username": "yuichi",
    "password": "MyPassword123",
    "email": "yuichi.yamazaki@g.softbank.co.jp",
    "role": "user"
}

def test_register_success():
    users.clear()
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"

    return None

def test_register_duplicate():
    users.clear()
    client.post("/register", json=test_user)
    response = client.post("/register", json=test_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "Error Code =400: This User is already registered."
    return None

def test_login_success():
    users.clear()
    client.post("/register", json=test_user)
    response = client.post("/login", json=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    return None

def test_login_wrong_password():
    users.clear()
    client.post("/register", json=test_user)
    wrong_user = {"username": "yuichi", "password": "aaabbb"}
    response = client.post("/login", json=wrong_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "token has not generated"
    
    return None

def test_get_profile_success():
    users.clear()
    client.post("/register", json=test_user)
    login_response = client.post("/login", json=test_user)
    token = login_response.json()["access_token"]
    response = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "yuichi"
    
    return None    

def test_profile_no_token():
    response = client.get("/profile")
    assert response.status_code == 422

    return None
