import requests
import jwt


BASE_URL = 'http://127.0.0.1:6969'

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




