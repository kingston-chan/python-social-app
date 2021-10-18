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
    
    response = requests.put(f"{url}/user/profile/setname/v1", json={"token": user_token, "name_first": 'John', "name_last":'Smith'})

    assert response.status_code == 200

# ==== Tests with incorrect/invalid input ==== #
def test_user_invalid_first_name():
    requests.delete(f"{url}/clear/v1")
    
    reg_response = register_user("email@email.com", "password", "Julian", "Winzer")

    user_token = reg_response["token"]
    
    response = requests.put(f"{url}/user/profile/setname/v1", json={"token": user_token, "name_first": '', "name_last":'Smith'})

    assert response.status_code == 400

def test_user_invalid_last_name():
    requests.delete(f"{url}/clear/v1")
    
    reg_response = register_user("email@email.com", "password", "Julian", "Winzer")

    user_token = reg_response["token"]
    
    response = requests.put(f"{url}/user/profile/setname/v1", json={"token": user_token, "name_first": 'John', "name_last":''})

    assert response.status_code == 400

# Invalid token
def test_invalid_token():
    requests.delete(f"{url}/clear/v1")
    response = requests.put(f"{url}/user/profile/setname/v1", json={ "token": "invalidtoken", "name_first": 'John', "name_last":'Smith'})
    assert response.status_code == 403
