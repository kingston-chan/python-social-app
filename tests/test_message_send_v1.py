import pytest
import requests
from src.config import url
import time
import json
from src.server import channel_invite, channel_join, channel_messages, message_send
import tests.route_helpers as rh

BASE_URL = url
## =====[ test_message_send_v1.py ]===== ##

# ==== Fixtures ==== #
@pytest.fixture
def clear():
    rh.clear()

@pytest.fixture
def user1():
    return rh.auth_register("user1@email.com", "password", "user", "name").json()

@pytest.fixture
def user2():
    return rh.auth_register("user2@email.com", "password", "user", "name").json()

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_invalid_channel(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id + 1, "Hello")
    assert message_response.status_code == 400

def test_message_too_long(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "A"*1500)
    assert message_response.status_code == 400

def test_message_too_short(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "")
    assert message_response.status_code == 400

## Access Error - 403 ##
def test_real_unauthorised_user(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    assert message_response.status_code == 403

def test_dummy_unauthorised_user(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(9999, channel_id, "Hello")
    assert message_response.status_code == 403

# ==== Tests - Valids ==== #
def test_one_user_sends_one_message_in_one_channel(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

def test_multiple_users_sends_multiple_messages_in_multiple_channels(clear, user1, user2):
    channel_id1 = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    channel_id2 = rh.channels_create(user1['token'], "chan_name2", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id1)
    rh.channel_join(user2['token'], channel_id2)

    message_response = rh.message_send(user1['token'], channel_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_send(user1['token'], channel_id1, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = rh.message_send(user2['token'], channel_id1, "Three")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 3

    message_response = rh.message_send(user2['token'], channel_id1, "Four")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 4

    message_response = rh.message_send(user1['token'], channel_id1, "Five")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 5

    message_response = rh.message_send(user1['token'], channel_id1, "Six")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 6

    message_response = rh.message_send(user2['token'], channel_id1, "Seven")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 7

    message_response = rh.message_send(user2['token'], channel_id1, "Eight")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 8

def test_one_user_sends_one_message_in_private_channel(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", False).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

def test_one_user_sends_one_message_in_private_and_public_channel(clear, user1):
    channel_id1 = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    channel_id2 = rh.channels_create(user1['token'], "chan_name2", False).json()['channel_id']

    message_response = rh.message_send(user1['token'], channel_id1, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_send(user1['token'], channel_id2, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

def test_one_user_invited_sends_one_messages_in_private_channel(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name2", False).json()['channel_id']
    rh.channel_invite(user1['token'], channel_id, user2['auth_user_id'])

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

def test_channel_messages_interaction(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
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
    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

