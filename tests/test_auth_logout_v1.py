import requests
import jwt
from src.config import port
from src.data_store import data_store

BASE_URL = 'http://127.0.0.1:' + str(port)

HASHCODE = "LKJNJLKOIHBOJHGIUFUTYRDUTRDSRESYTRDYOJJHBIUYTF"

def test_logout():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

 
    requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response = requests.post(f"{BASE_URL}/auth/login/v2", json=user_data)
    response_data = response.json()

    

    requests.post(f"{BASE_URL}/auth/logout/v1", json=response_data["token"])

    assert response.status_code == 200

def test_invalid_token():
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.post(f"{BASE_URL}/auth/logout/v1", json="invalidToken")
    assert response.status_code == 403
    


