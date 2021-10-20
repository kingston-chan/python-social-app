import requests
import jwt
from src.config import port
from src.data_store import data_store

BASE_URL = 'http://127.0.0.1:' + str(port)

HASHCODE = "LKJNJLKOIHBOJHGIUFUTYRDUTRDSRESYTRDYOJJHBIUYTF"

# Invalid input tests:

def test_login_invalid_email():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)

    response = requests.post(f"{BASE_URL}/auth/login/v2", json={"email": 'email', "password": 'password'})

    assert response.status_code == 400

def test_login_invalid_password():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)

    response = requests.post(f"{BASE_URL}/auth/login/v2", json={"email": 'email@email.com', "password": 'pass'})

    assert response.status_code == 400


# Valid input tests:

def test_login_valid_input():
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
    

    assert response_data["auth_user_id"] == 1

    assert jwt.decode(response_data["token"], HASHCODE, algorithms=['HS256']) == {'user_id': 1, 'session_id': 2}



def test_login_valid_multiple_times():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    
    
    requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)

    requests.post(f"{BASE_URL}/auth/login/v2", json=user_data)
    
    response = requests.post(f"{BASE_URL}/auth/login/v2", json=user_data)
    response_data = response.json()
    

    assert response_data["auth_user_id"] == 1

    assert jwt.decode(response_data["token"], HASHCODE, algorithms=['HS256']) == {'user_id': 1, 'session_id': 3}

def test_login_valid_multiple_users():
    requests.delete(f"{BASE_URL}/clear/v1")

    user1_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    user2_data = {
        "email": "email2@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    
    
    requests.post(f"{BASE_URL}/auth/register/v2", json=user1_data)
    requests.post(f"{BASE_URL}/auth/register/v2", json=user2_data)

    
    
    response = requests.post(f"{BASE_URL}/auth/login/v2", json=user1_data)
    response_data = response.json()
    

    assert response_data["auth_user_id"] == 1

    assert jwt.decode(response_data["token"], HASHCODE, algorithms=['HS256']) == {'user_id': 1, 'session_id': 3}
