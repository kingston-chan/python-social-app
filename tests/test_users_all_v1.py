import pytest, requests

BASE_URL = 'http://127.0.0.1:8080'

# ==== Tests with correct input ==== #

# Lists all users given valid token
def test_list_all_users():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_info = {
        "email": "random@gmail.com", 
        "password": "123abc!@#", 
        "name_first": "John", 
        "name_last": "Smith"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_info)
    response_data = response.json()
    user_token1 = response_data["token"]
    user1_id = response_data["auth_user_id"]

    user_info["email"] = "random1@gmail.com"
    user_info["name_first"] = "Bob"
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_info)
    response_data = response.json()
    user2_id = response_data["auth_user_id"] 

    user_info["email"] = "random2@gmail.com"
    user_info["name_first"] = "Dan"
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_info)
    response_data = response.json()
    user3_id = response_data["auth_user_id"] 

    response = requests.get(f"{BASE_URL}/users/all/v1", json={ "token": user_token1 })
    assert response.status_code == 200

    response_data = response.json()

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
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.get(f"{BASE_URL}/users/all/v1", json={ "token": "invalidtoken" })
    assert response.status_code == 400