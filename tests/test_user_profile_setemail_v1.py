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
def test_user_valid():
    requests.delete(f"{url}/clear/v1")
    
    reg_response = register_user("email@email.com", "password", "Julian", "Winzer")

    user_token = reg_response["token"]
    
    response = requests.put(f"{url}/user/profile/setemail/v1", json={"token": user_token, "email": 'newemail@newemail.com'})

    assert response.status_code == 200

# ==== Tests with incorrect/invalid input ==== #
def test_user_invalid_email():
    requests.delete(f"{url}/clear/v1")
    
    reg_response = register_user("email@email.com", "password", "Julian", "Winzer")

    user_token = reg_response["token"]
    
    response = requests.put(f"{url}/user/profile/setemail/v1", json={"token": user_token, "email": 'invalid'})

    assert response.status_code == 400

# Invalid token
def test_invalid_token():
    requests.delete(f"{url}/clear/v1")
    response = requests.put(f"{url}/user/profile/setemail/v1", json={ "token": "invalidtoken", "email": 'newemail@newemail.com'})
    assert response.status_code == 403
