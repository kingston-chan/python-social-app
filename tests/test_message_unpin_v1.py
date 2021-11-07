import pytest
import requests
from src.config import url
import time
import json
import tests.route_helpers as rh

BASE_URL = url

## =====[ test_message_unpin_v1.py ]===== ##

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

@pytest.fixture
def user3():
    return rh.auth_register("user3@email.com", "password", "user", "name").json()

# ==== Helper Function ==== #
def create_channel_send_message_and_pin_message(token, invites=None):
    channel_id = rh.channels_create(token, "chan_name", True).json()['channel_id']
    if invites != None:
        for invite in invites:
            rh.channel_invite(token, channel_id, invite)
    message_response = rh.message_send(token, channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_pin(token, response_data['message_id'])
    assert message_response.status_code == 200

    return response_data['message_id']

def create_dm_send_message_and_pin_message(token, users=[]):
    dm_id = rh.dm_create(token, users).json()['dm_id']
    message_response = rh.message_senddm(token, dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_pin(token, response_data['message_id'])
    assert message_response.status_code == 200

    return response_data['message_id']

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_message_not_valid_in_channel(clear, user1):
    message_id = create_channel_send_message_and_pin_message(user1['token'])
    message_response = rh.message_unpin(user1['token'], message_id + 1)
    assert message_response.status_code == 400

def test_message_not_valid_in_dm(clear, user1, user2):
    message_id = create_dm_send_message_and_pin_message(user1['token'], [user2['auth_user_id']])
    message_response = rh.message_unpin(user1['token'], message_id + 1)
    assert message_response.status_code == 400

def test_user_not_in_channel(clear, user1, user2):
    message_id = create_channel_send_message_and_pin_message(user1['token'])
    message_response = rh.message_unpin(user2['token'], message_id)
    assert message_response.status_code == 400

def test_user_not_in_dm(clear, user1, user2, user3):
    message_id = create_dm_send_message_and_pin_message(user1['token'], [user2['auth_user_id']])
    message_response = rh.message_unpin(user3['token'], message_id)
    assert message_response.status_code == 400

def test_message_already_unpinned_in_channel(clear, user1):
    message_id = create_channel_send_message_and_pin_message(user1['token'])
    message_response = rh.message_unpin(user1['token'], message_id)
    assert message_response.status_code == 200
    message_response = rh.message_unpin(user1['token'], message_id)
    assert message_response.status_code == 400

def test_message_already_unpinned_in_dm(clear, user1, user2):
    message_id = create_dm_send_message_and_pin_message(user1['token'], [user2['auth_user_id']])
    message_response = rh.message_unpin(user1['token'], message_id)
    assert message_response.status_code == 200
    message_response = rh.message_unpin(user1['token'], message_id)
    assert message_response.status_code == 400

def test_unpin_message_in_removed_dm(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    rh.dm_remove(user1['token'], dm_id)

    message_response = rh.message_unpin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 400

## Access Error - 403 ##
def test_unauthorised_user_in_channel(clear, user1, user2):
    message_id = create_channel_send_message_and_pin_message(user1['token'], [user2['auth_user_id']])
    message_response = rh.message_unpin(user2['token'], message_id)
    assert message_response.status_code == 403

def test_authorised_non_owner_messaged_in_channel(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_invite(user1['token'], channel_id, user2['auth_user_id'])
    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_unpin(user2['token'], response_data['message_id'])
    assert message_response.status_code == 403

def test_unauthorised_user_in_dm(clear, user1, user2):
    message_id = create_dm_send_message_and_pin_message(user1['token'], [user2['auth_user_id']])

    message_response = rh.message_unpin(user2['token'], message_id)
    assert message_response.status_code == 403

def test_authorised_non_owner_messaged_in_dm(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user2['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_unpin(user2['token'], response_data['message_id'])
    assert message_response.status_code == 403

# ==== Tests - Valids ==== #
def test_valid_pin_in_channel(clear, user1):
    message_id = create_channel_send_message_and_pin_message(user1['token'])
    message_response = rh.message_unpin(user1['token'], message_id)
    assert message_response.status_code == 200

def test_valid_pin_in_dm(clear, user1, user2):
    message_id = create_dm_send_message_and_pin_message(user1['token'], [user2['auth_user_id']])
    message_response = rh.message_unpin(user1['token'], message_id)
    assert message_response.status_code == 200

def test_one_person_pinning_multiple_messages(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']

    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data1 = message_response.json()
    assert message_response.status_code == 200
    assert response_data1['message_id'] == 1

    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data2 = message_response.json()
    assert message_response.status_code == 200
    assert response_data2['message_id'] == 2

    message_response = rh.message_pin(user1['token'], response_data1['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_pin(user1['token'], response_data2['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_unpin(user1['token'], response_data1['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_unpin(user1['token'], response_data2['message_id'])
    assert message_response.status_code == 200

def test_pin_in_dm_and_in_channel(clear, user1, user2):
    message_id = create_channel_send_message_and_pin_message(user1['token'])
    message_response = rh.message_unpin(user1['token'], message_id)
    assert message_response.status_code == 200

    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_unpin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

def channel_messages_interaction(clear, user1):
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
                "time_created": int(time.time()),
                "reacts": [],
                "is_pinned": False,
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
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']
    
    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "Hello",
                "time_created": int(time.time()),
                "reacts": [],
                "is_pinned": True,
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
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

    message_response = rh.message_unpin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "Hello",
                "time_created": int(time.time()),
                "reacts": [],
                "is_pinned": False,
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
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

def dm_messages_interaction(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    messages_response = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "Hello",
                "time_created": int(time.time()),
                "reacts": [],
                "is_pinned": False,
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
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    messages_response = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "Hello",
                "time_created": int(time.time()),
                "reacts": [],
                "is_pinned": True,
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
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

    message_response = rh.message_unpin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    messages_response = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "Hello",
                "time_created": int(time.time()),
                "reacts": [],
                "is_pinned": False,
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
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

def test_multiple_pins_in_multiple_channels(clear, user1):
    channel_id1 = rh.channels_create(user1['token'], "chan_name1", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id1, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_unpin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    channel_id2 = rh.channels_create(user1['token'], "chan_name2", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id2, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_unpin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

def test_multiple_pins_in_multiple_dms(clear, user1, user2):
    dm_id1 = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id1, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_unpin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    dm_id2 = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id2, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = rh.message_pin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200

    message_response = rh.message_unpin(user1['token'], response_data['message_id'])
    assert message_response.status_code == 200