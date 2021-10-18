import pytest, requests
from src.config import url

# ==== Helper function ==== #
def register_user(email, password, first_name, last_name):
    user_info = {
        "email": email, 
        "password": password, 
        "name_first": first_name, 
        "name_last": last_name
    }
    return requests.post(f"{url}/auth/register/v2", json=user_info).json()

# ==== Tests with correct input ==== #

# Lists all users given valid token
def test_return_profile():
    requests.delete(f"{url}/clear/v1")
    
    reg_response = register_user("email@gmail.com", "password", "Julian", "Winzer")
    assert reg_response.status_code == 200

    user_token = reg_response["token"]
    user_id = reg_response["auth_user_id"]
    
    response = requests.get(f"{url}/users/profile/v1", params={"token": user_token, "u_id": user_id})
    response_data = response.json()

    assert response_data == {"user_id": 1, "email": 'email@email.com', "name_first": 'Julian', "name_last": 'Winzer', "handle": 'julianwinzer'}

# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    requests.delete(f"{url}/clear/v1")
    response = requests.get(f"{url}/users/profile/v1", params={ "token": "invalidtoken", "user_id": 1})
    assert response.status_code == 403
