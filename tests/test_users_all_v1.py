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
def test_list_all_users():
    requests.delete(f"{url}/clear/v1")
    
    response_data = register_user("random@gmail.com", "123abc!@#", "John", "Smith")
    user_token1 = response_data["token"]
    user1_id = response_data["auth_user_id"]
    response_data = register_user("random1@gmail.com", "123abc!@#", "Bob", "Smith")
    user2_id = response_data["auth_user_id"]

    response_data = register_user("random2@gmail.com", "123abc!@#", "Dan", "Smith")
    user3_id = response_data["auth_user_id"] 

    response = requests.get(f"{url}/users/all/v1", params={ "token": user_token1 })
    assert response.status_code == 200

    response_data = response.json()
    print(response_data)
    assert len(response_data["users"]) == 3

    assert response_data["users"][0]["u_id"] == user1_id
    assert response_data["users"][1]["u_id"] == user2_id
    assert response_data["users"][2]["u_id"] == user3_id

    assert response_data["users"][0]["email"] == "random@gmail.com"
    assert response_data["users"][1]["email"] == "random1@gmail.com"
    assert response_data["users"][2]["email"] == "random2@gmail.com"

    assert response_data["users"][0]["name_first"] == "John"
    assert response_data["users"][1]["name_first"] == "Bob"
    assert response_data["users"][2]["name_first"] == "Dan"

# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    requests.delete(f"{url}/clear/v1")
    response = requests.get(f"{url}/users/all/v1", params={ "token": "invalidtoken" })
    assert response.status_code == 403

# Invalid session
# def test_invalid_session():
#     requests.delete(f"{url}/clear/v1")
#     user_token = register_user("random@gmail.com", "123abc!@#", "John", "Smith")["token"]
#     requests.post(f"{url}/auth/logout/v1", json={ "token": user_token })
#     response = requests.get(f"{url}/users/all/v1", params={ "token": user_token })
#     assert response.status_code == 403