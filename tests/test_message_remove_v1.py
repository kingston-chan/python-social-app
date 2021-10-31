import pytest
import requests
from src.config import url
import time
import json
import tests.route_helpers as rh

BASE_URL = url
## =====[ test_message_remove_v1.py ]===== ##

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

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_invalid_fake_message_id(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']

    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_remove(user1['token'], response_data['message_id'] + 1)
    assert message_response.status_code == 400

def test_invalid_fake_message_id_2(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']

    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_remove(user1['token'], response_data['message_id'] + 1)
    assert message_response.status_code == 400

def test_user_left_and_tries_to_remove(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    rh.channel_leave(user2['token'], channel_id)

    message_response = rh.message_remove(user2['token'], message_id)
    assert message_response.status_code == 400

def test_owner_left_and_tries_to_remove(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)

    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    rh.channel_leave(user1['token'], channel_id)

    message_response = rh.message_remove(user1['token'], message_id)
    assert message_response.status_code == 400

def test_user_not_in_dm(clear, user1, user2, user3):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']

    message_response = rh.message_senddm(user2['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_remove(user3['token'], response_data['message_id'])
    assert message_response.status_code == 400

def test_removed_dm(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']

    message_response = rh.message_senddm(user2['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    rh.dm_remove(user1['token'], dm_id)

    remove_response = rh.message_remove(user2['token'], message_id)
    assert remove_response.status_code == 400  

## Access Error - 403 ##
def test_unauthorised_user(clear, user1, user2, user3):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)
    rh.channel_join(user3['token'], channel_id)

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_remove(user3['token'], response_data['message_id'])
    assert message_response.status_code == 403

def test_user_not_owner(clear, user1, user2, user3):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)
    rh.channel_join(user3['token'], channel_id)

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_remove(user3['token'], response_data['message_id'])
    assert message_response.status_code == 403

def test_user_not_owner_in_dm(clear, user1, user2, user3):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id'], user3['auth_user_id']]).json()['dm_id']

    message_response = rh.message_senddm(user2['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_remove(user3['token'], response_data['message_id'])
    assert message_response.status_code == 403

# ==== Tests - Valids ==== #
def test_one_user_removes_one_message_in_one_channel(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_remove(user1['token'], message_id)
    assert message_response.status_code == 200

def test_multiple_users_removes_multiple_messages_in_multiple_channels(clear, user1, user2):
    channel_id1 = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    channel_id2 = rh.channels_create(user1['token'], "chan_name2", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id1)
    rh.channel_join(user2['token'], channel_id2)

    message_response = rh.message_send(user1['token'], channel_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id1 = response_data['message_id']

    message_response = rh.message_send(user1['token'], channel_id1, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2
    message_id2 = response_data['message_id']

    message_response = rh.message_send(user2['token'], channel_id1, "Three")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 3
    message_id3 = response_data['message_id']

    message_response = rh.message_send(user2['token'], channel_id1, "Four")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 4
    message_id4 = response_data['message_id']

    message_response = rh.message_send(user1['token'], channel_id1, "Five")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 5
    message_id5 = response_data['message_id']

    message_response = rh.message_send(user1['token'], channel_id1, "Six")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 6
    message_id6 = response_data['message_id']

    message_response = rh.message_send(user2['token'], channel_id1, "Seven")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 7
    message_id7 = response_data['message_id']

    message_response = rh.message_send(user2['token'], channel_id1, "Eight")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 8
    message_id8 = response_data['message_id']

    message_response = rh.message_remove(user1['token'], message_id1)
    assert message_response.status_code == 200

    message_response = rh.message_remove(user1['token'], message_id2)
    assert message_response.status_code == 200

    message_response = rh.message_remove(user2['token'], message_id3)
    assert message_response.status_code == 200

    message_response = rh.message_remove(user2['token'], message_id4)
    assert message_response.status_code == 200

    message_response = rh.message_remove(user1['token'], message_id5)
    assert message_response.status_code == 200

    message_response = rh.message_remove(user1['token'], message_id6)
    assert message_response.status_code == 200

    message_response = rh.message_remove(user2['token'], message_id7)
    assert message_response.status_code == 200

    message_response = rh.message_remove(user2['token'], message_id8)
    assert message_response.status_code == 200

def test_send_edit_remove_message(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_edit(user1['token'], message_id, "Hey there")
    assert message_response.status_code == 200

    message_response = rh.message_remove(user1['token'], message_id)
    assert message_response.status_code == 200

def test_owner_removes_another_users_message(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_remove(user1['token'], message_id)
    assert message_response.status_code == 200

def test_global_owner_removes_another_users_message(clear, user1, user2, user3):
    channel_id = rh.channels_create(user2['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user3['token'], channel_id)
    rh.channel_join(user1['token'], channel_id)

    message_response = rh.message_send(user3['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_remove(user1['token'], message_id)
    assert message_response.status_code == 200

def test_one_user_removes_one_message_in_private_channel(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", False).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_remove(user1['token'], message_id)
    assert message_response.status_code == 200

def test_one_user_removes_one_message_in_private_and_public_channel(clear, user1):
    channel_id1 = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    channel_id2 = rh.channels_create(user1['token'], "chan_name2", False).json()['channel_id']

    message_response = rh.message_send(user1['token'], channel_id1, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id1 = response_data['message_id']

    message_response = rh.message_send(user1['token'], channel_id2, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2
    message_id2 = response_data['message_id']

    message_response = rh.message_remove(user1['token'], message_id1)
    assert message_response.status_code == 200
    message_response = rh.message_remove(user1['token'], message_id2)
    assert message_response.status_code == 200

def test_one_user_invited_removes_one_messages_in_private_channel(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name2", False).json()['channel_id']
    rh.channel_invite(user1['token'], channel_id, user2['auth_user_id'])

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_remove(user1['token'], message_id)
    assert message_response.status_code == 200

def test_user_becomes_owner_removes(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name2", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)

    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    rh.channel_addowner(user1['token'], channel_id, user2['auth_user_id'])

    message_response = rh.message_remove(user2['token'], message_id)
    assert message_response.status_code == 200

def test_channel_messages_interaction(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

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
                "is_pinned": False
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

    message_response = rh.message_remove(user1['token'], message_id)
    assert message_response.status_code == 200

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

def test_channel_messages_interaction2(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id1 = response_data['message_id']
    time_created1 = int(time.time())

    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2
    message_id2 = response_data['message_id']
    time_created2 = int(time.time())

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 2,
                "u_id": user1['auth_user_id'],
                "message": "Hello",
                "time_created": time_created2,
                "reacts": [],
                "is_pinned": False,
            }, 
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "Hello",
                "time_created": time_created1,
                "reacts": [],
                "is_pinned": False 
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

    message_response = rh.message_remove(user1['token'], message_id2)
    assert message_response.status_code == 200

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "Hello",
                "time_created": time_created1,
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

    message_response = rh.message_remove(user1['token'], message_id1)
    assert message_response.status_code == 200

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }

    assert response_data == expected_result

def test_one_user_removes_one_message_in_one_dm(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = dm_messages.json()
    expected_result = {
        "messages": [
            {
                "message_id": message_id,
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

    message_response = rh.message_remove(user1['token'], message_id)
    assert message_response.status_code == 200

    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = dm_messages.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert expected_result == response_data

def test_one_user_removes_in_channel_and_dm(clear, user1, user2, user3):
    # Edits in channel
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    messages = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages.json()
    expected_result = {
        "messages": [
            {
                "message_id": message_id,
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

    message = rh.message_remove(user1['token'], message_id)
    assert message.status_code == 200

    messages = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert expected_result == response_data

    # Creates a middle DM
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    dm_message = rh.message_senddm(user1['token'], dm_id, "Hello")
    message_id = dm_message.json()['message_id']
    assert message_id == 2
    assert dm_message.status_code == 200

    # Creates a DM and edits a sent message in it
    dm_id = rh.dm_create(user1['token'], [user3['auth_user_id']]).json()['dm_id']
    dm_message = rh.message_senddm(user3['token'], dm_id, "Hello")
    message_id = dm_message.json()['message_id']
    assert message_id == 3
    assert dm_message.status_code == 200
    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = dm_messages.json()
    expected_result = {
        "messages": [
            {
                "message_id": message_id,
                "u_id": user3['auth_user_id'],
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

    dm_message = rh.message_remove(user1['token'], message_id)
    assert dm_message.status_code == 200

    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = dm_messages.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert expected_result == response_data