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

# ==== Helper functions ==== #

def create_channel(token, name, is_public):
    channel_info = {
        "token": token, 
        "name": name, 
        "is_public": is_public
    }

    return requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)

def list_channels(token):
    return requests.get(f"{BASE_URL}/channels/list/v2", params={ "token": token })

# ==== Tests with correct input ==== #

# Creates a channel successfully
def test_can_create_channel(clear_and_register):
    response = create_channel(clear_and_register, "channel1", "True")
    assert response.status_code == 200
    
    response_data = response.json()
    channel1_id = response_data['channel_id']

    response = list_channels(clear_and_register)
    response_data = response.json()
    
    assert response_data["channels"][0]["channel_id"] == channel1_id
    assert response_data["channels"][0]["name"] == "channel1"


# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    requests.delete(f"{BASE_URL}/clear/v1")
    response = create_channel("invalidtoken", "channel1", "True")
    assert response.status_code == 403

# Invalid name (less than 1 character, more than 20 characters)
def test_invalid_name(clear_and_register):

    response = create_channel(clear_and_register, "", "True")
    assert response.status_code == 400

    response = create_channel(clear_and_register, "morethantwentycharacters", "True")
    assert response.status_code == 400

    response = create_channel(clear_and_register, "                    ", "True")
    assert response.status_code == 400

# Channel name already exists
def test_channel_name_already_exists(clear_and_register):
    create_channel(clear_and_register, "channel1", "True")
    response = create_channel(clear_and_register, "channel1", "True")
    assert response.status_code == 400

    response = create_channel(clear_and_register, "CHANNEL1", "True")
    assert response.status_code == 400

    response = create_channel(clear_and_register, "     CHannEL1     ", "True")
    assert response.status_code == 400

# Invalid session id
def test_invalid_session(clear_and_register):
    requests.post(f"{BASE_URL}/auth/logout/v1", json={ "token": clear_and_register })
    response = create_channel(clear_and_register, "channel1", "True")
    assert response.status_code == 403