import requests, pytest

BASE_URL = 'http://127.0.0.1:8080'

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

    return requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info).json()["channel_id"]

# Lists all channels user is in
def list_channels(token):
    return requests.get(f"{BASE_URL}/channels/list/v2", params={ "token": token }).json()

# Joins the channel of given channel_id
def join_channel(token, channel_id):
    return requests.post(f"{BASE_URL}/channel/join/v2", json={ "token": token, "channel_id": channel_id })

# Lists all existing channels
def list_all_channels(token):
    return requests.get(f"{BASE_URL}/channels/list/v2", params={ "token": token }).json()

# Leave the given channel
def leave_channel(token, channel_id):
    return requests.post(f"{BASE_URL}/channels/list/v2", json={ "token": token, "channel_id": channel_id })

@pytest.fixture
def clear_and_register():
    requests.delete(f"{BASE_URL}/clear/v1")
    return register_user("random@gmail.com", "123abc!@#", "John", "Smith")

# ==== Tests with correct input ==== #

# Owner is able to leave the channel, but channel still exists, even with no members
def test_owner_leaves_channel_still_exists(clear_and_register):
    channel1_id = create_channel(clear_and_register, "channel1", "True")
    
    leave_channel(clear_and_register, channel1_id)
    
    response_data = list_channels(clear_and_register)
    assert len(response_data["channels"]) == 0
    
    response_data = list_all_channels(clear_and_register)
    assert len(response_data["channels"]) == 1

# ==== Tests with incorrect/invalid input ==== #

# Invalid token, but valid channel id
def test_invalid_token(clear_and_register):
    channel1_id = create_channel(clear_and_register, "channel1", "True")
    response = leave_channel("invalidtoken", channel1_id)
    assert response.status_code == 403

# Valid token but invalid channel id
def test_invalid_channel_id(clear_and_register):
    response = leave_channel(clear_and_register, "invalidtoken")
    assert response == 400

# Valid token and channel_id but token's payload contains unauthorised id
def test_unauthorised_id(clear_and_register):
    channel1_id = create_channel(clear_and_register, "channel1", "True")
    user2_token = register_user("random2@gmail.com", "123abc!@#", "Bob", "Smith")["token"]
    response = leave_channel(user2_token, channel1_id)
    assert response.status_code == 403

