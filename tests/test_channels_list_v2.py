import requests, pytest, json
from src.config import port

BASE_URL = 'http://127.0.0.1:' + str(port)


# ==== Helper functions ==== #

# Registers a user
def register_user(email, password, first_name, last_name):
    user_info = {
        "email": email, 
        "password": password, 
        "name_first": first_name, 
        "name_last": last_name
    }
    return requests.post(f"{BASE_URL}/auth/register/v2", json=user_info).json()


# Creates channel and returns created channel_id
def create_channel(token, name, is_public):
    channel_info = {
        "token": token, 
        "name": name, 
        "is_public": is_public
    }
    payload = json.dumps(channel_info)
    return requests.post(f"{BASE_URL}/channels/create/v2", json=payload).json()["channel_id"]

# Lists all channels user is in
def list_channels(token):
    return requests.get(f"{BASE_URL}/channels/list/v2", params={ "token": token })

@pytest.fixture
def clear_and_register():
    requests.delete(f"{BASE_URL}/clear/v1")
    return register_user("random@gmail.com", "123abc!@#", "John", "Smith")['token']


# ==== Tests with correct input ==== #

# List channels authorised user is in
def test_user_list_channel(clear_and_register):
    channel1_id = create_channel(clear_and_register, "channel1", True)
    channel2_id = create_channel(clear_and_register, "channel2", True)

    response_data = list_channels(clear_and_register).json()
    
    assert len(response_data["channels"]) == 2
    assert response_data["channels"][0]["channel_id"] == channel1_id
    assert response_data["channels"][1]["channel_id"] == channel2_id

# List only channels authorised user is in, including private ones
def test_only_list_authorised_user_channels(clear_and_register):
    user_token2 = register_user("random2@gmail.com", "123abc!@#", "Bob", "Smith")['token']

    channel1_id = create_channel(clear_and_register, "channel1", False)

    create_channel(user_token2, "Channel2", True)

    response_data = list_channels(clear_and_register).json()
    assert len(response_data["channels"]) == 1
    assert response_data["channels"][0]["channel_id"] == channel1_id

# Empty list if user is not in any channels
def test_user_not_in_any_channels(clear_and_register):
    response_data = list_channels(clear_and_register)
    assert len(response_data["channels"]) == 0
    assert response_data["channels"] == []
    

# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    response = list_channels("invalidtoken")
    assert response.status_code == 400

# Invalid session
def test_invalid_session(clear_and_register):
    create_channel(clear_and_register, "channel1", True)
    requests.post(f"{BASE_URL}/auth/logout/v1", json={ "token": clear_and_register })
    response = list_channels(clear_and_register)
    assert response.status_code == 403
    

