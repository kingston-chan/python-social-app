import requests, pytest

BASE_URL = 'http://127.0.0.1:8080'

@pytest.fixture
def clear_and_register():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_info = {
        "email": "random@gmail.com", 
        "password": "123abc!@#", 
        "name_first": "John", 
        "name_last": "Smith"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_info)
    response_data = response.json()
    return response_data['token']

# ==== Tests with correct input ==== #

# Creates a channel successfully
def test_can_create_channel(clear_and_register):
    user_token = clear_and_register

    channel_info = {
        "token": user_token, 
        "name": "channel1", 
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    assert response.status_code == 200
    
    response_data = response.json()
    channel1_id = response_data['channel_id']

    response = requests.get(f"{BASE_URL}/channels/list/v2", params={ "token": user_token })
    response_data = response.json()
    
    assert response_data["channels"][0]["channel_id"] == channel1_id
    assert response_data["channels"][0]["name"] == "channel1"


# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    requests.delete(f"{BASE_URL}/clear/v1")
    channel_info = {
        "token": "invalidtoken", 
        "name": "channel1", 
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    assert response.status_code == 400



# Invalid name (less than 1 character, more than 20 characters)
def test_invalid_name(clear_and_register):
    user_token = clear_and_register

    channel_info = {
        "token": user_token, 
        "name": "", 
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    assert response.status_code == 400

    channel_info["name"] = "morethantwentycharacters"
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    assert response.status_code == 400

    channel_info["name"] = "                    "
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    assert response.status_code == 400


# Channel name already exists
def test_channel_name_already_exists(clear_and_register):
    user_token = clear_and_register

    channel_info = {
        "token": user_token, 
        "name": "channel1", 
        "is_public": "True"
    }

    requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    assert response.status_code == 400
    
    channel_info["name"] = "CHANNEL1"
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    assert response.status_code == 400
    
    channel_info["name"] = "     CHannEL1     "
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    assert response.status_code == 400