import pytest
import requests
from src.config import url
import datetime
import json

BASE_URL = url
## =====[ test_message_send_v1.py ]===== ##

# ==== Fixtures ==== #
@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")

@pytest.fixture
def user1():
    user_dict = {
        "email": "user1@email.com",
        "password": "password",
        "name_first": "user",
        "name_last": "name"
    }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_dict)
    print(response.json())
    return response.json()

@pytest.fixture
def user2():
    user_dict = {
        "email": "user2@email.com",
        "password": "password",
        "name_first": "user",
        "name_last": "name"
    }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_dict)
    return response.json()

# ==== Helper functions ==== #
def create_channel(token, name, is_public):
    channel_info = {
        "token": token, 
        "name": name, 
        "is_public": is_public
    }
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response_data = response.json()
    return int(response_data['channel_id'])

def join_channel(token, channel_id):
    channel_info = {
        "token": token, 
        "channel_id": channel_id,
    }
    return requests.post(f"{BASE_URL}/channels/join/v2", json=channel_info)

def send_message(token, channel_id, message):
    message_dict = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(f"{BASE_URL}/message/send/v1", json=message_dict)
    return response

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_invalid_channel(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", True)
    message_response = send_message(user1['token'], channel_id + 1, "Hello")
    assert message_response.status_code == 400

def test_message_too_long(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", True)
    message_response = send_message(user1['token'], channel_id, "A"*1500)
    assert message_response.status_code == 400

def test_message_too_short(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", True)
    message_response = send_message(user1['token'], channel_id, "")
    assert message_response.status_code == 400

## Access Error - 403 ##
def test_real_unauthorised_user(clear, user1, user2):
    channel_id = create_channel(user1['token'], "chan_name", True)
    message_response = send_message(user2['token'], channel_id, "Hello")
    assert message_response.status_code == 403

def test_dummy_unauthorised_user(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", True)
    message_response = send_message(9999, channel_id, "Hello")
    assert message_response.status_code == 403

# ==== Tests - Valids ==== #
def test_one_user_sends_one_message_in_one_channel(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", True)
    message_response = send_message(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

def test_one_user_sends_one_message_in_multiple_channels(clear, user1):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    channel_id2 = create_channel(user1['token'], "chan_name2", True)

    message_response = send_message(user1['token'], channel_id1, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user1['token'], channel_id2, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

def test_one_user_sends_multiple_messages_in_one_channel(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", True)
    
    message_response = send_message(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user1['token'], channel_id, "Hello again")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

def test_one_user_sends_multiple_messages_in_multiple_channels(clear, user1):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    channel_id2 = create_channel(user1['token'], "chan_name2", True)

    message_response = send_message(user1['token'], channel_id1, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user1['token'], channel_id2, "Hello again")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = send_message(user1['token'], channel_id1, "Hello for the third time")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 3

    message_response = send_message(user1['token'], channel_id2, "Final hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 4

def test_multiple_users_sends_one_message_in_one_channel(clear, user1, user2):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    join_channel(user2['token'], channel_id1)

    message_response = send_message(user1['token'], channel_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user1['token'], channel_id1, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2
    
def test_multiple_users_sends_one_message_in_multiple_channels(clear, user1, user2):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    join_channel(user2['token'], channel_id1)

    message_response = send_message(user1['token'], channel_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user1['token'], channel_id1, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

def test_multiple_users_sends_multiple_messages_in_one_channel(clear, user1, user2):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    join_channel(user2['token'], channel_id1)

    message_response = send_message(user1['token'], channel_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user1['token'], channel_id1, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = send_message(user2['token'], channel_id1, "Three")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 3

    message_response = send_message(user2['token'], channel_id1, "Four")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 4

def test_multiple_users_sends_multiple_messages_in_multiple_channels(clear, user1, user2):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    channel_id2 = create_channel(user1['token'], "chan_name2", True)
    join_channel(user2['token'], channel_id1)
    join_channel(user2['token'], channel_id2)

    message_response = send_message(user1['token'], channel_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user1['token'], channel_id2, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = send_message(user2['token'], channel_id1, "Three")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 3

    message_response = send_message(user2['token'], channel_id2, "Four")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 4

# ==== Future Tests for Future Functions ==== #

def test_one_user_sends_one_message_in_private_channel(clear, user1):
    pass

def test_one_user_sends_one_message_in_private_and_public_channel(clear, user1):
    pass

