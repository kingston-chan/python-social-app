import pytest
import requests
from src.config import url
import time
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
    return requests.post(f"{BASE_URL}/channel/join/v2", json=channel_info)

def invite_member_to_channel(token, channel_id, u_id):
    invite_info = {
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id,
    }
    return requests.post(f"{BASE_URL}/channel/invite/v2", json=invite_info)

def send_message(token, channel_id, message):
    message_dict = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    return requests.post(f"{BASE_URL}/message/send/v1", json=message_dict)

def channel_messages(token, channel_id, start):
    messages_info = {
        "token": token,
        "channel_id": channel_id,
        "start": start 
    }
    return requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_info)

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
def test_one_user_edits_one_message_in_one_channel(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", True)
    message_response = send_message(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

def test_one_user_edits_one_message_in_multiple_channels(clear, user1):
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

def test_one_user_edits_multiple_messages_in_one_channel(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", True)
    
    message_response = send_message(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

def test_one_user_edits_multiple_messages_in_multiple_channels(clear, user1):
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

def test_multiple_users_edits_one_message_in_one_channel(clear, user1, user2):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    join_channel(user2['token'], channel_id1)

    message_response = send_message(user1['token'], channel_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user2['token'], channel_id1, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

def test_multiple_users_edits_one_message_in_multiple_channels(clear, user1, user2):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    channel_id2 = create_channel(user1['token'], "chan_name2", True)
    join_channel(user2['token'], channel_id1)
    join_channel(user2['token'], channel_id2)

    message_response = send_message(user1['token'], channel_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user2['token'], channel_id1, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = send_message(user1['token'], channel_id2, "Three")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 3

    message_response = send_message(user2['token'], channel_id2, "Four")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 4

def test_multiple_users_edits_multiple_messages_in_one_channel(clear, user1, user2):
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

def test_multiple_users_edits_multiple_messages_in_multiple_channels(clear, user1, user2):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    channel_id2 = create_channel(user1['token'], "chan_name2", True)
    join_channel(user2['token'], channel_id1)
    join_channel(user2['token'], channel_id2)

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

    message_response = send_message(user1['token'], channel_id1, "Five")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 5

    message_response = send_message(user1['token'], channel_id1, "Six")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 6

    message_response = send_message(user2['token'], channel_id1, "Seven")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 7

    message_response = send_message(user2['token'], channel_id1, "Eight")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 8

def test_one_user_sends_one_message_in_private_channel(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", False)
    message_response = send_message(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

def test_one_user_sends_one_message_in_private_and_public_channel(clear, user1):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    channel_id2 = create_channel(user1['token'], "chan_name2", False)

    message_response = send_message(user1['token'], channel_id1, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_message(user1['token'], channel_id2, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

def test_one_user_invited_sends_one_messages_in_private_channel(clear, user1, user2):
    channel_id = create_channel(user1['token'], "chan_name2", False)
    invite_member_to_channel(user1['token'], channel_id, user2['auth_user_id'])

    message_response = send_message(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

def test_channel_messages_interaction(clear, user1):
    channel_id = create_channel(user1['token'], "chan_name", True)
    message_response = send_message(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    messages_response = channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "Hello",
                "time_created": int(time.time()) 
            }
        ],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result