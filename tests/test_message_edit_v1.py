import pytest
import requests
from src.config import url
import time
import json
from src.server import channel_addowner, channel_invite, channel_leave, channel_messages, channel_removeowner, dm_create, dm_messages, dm_remove, message_edit, message_send, message_senddm
import tests.route_helpers as rh

BASE_URL = url
## =====[ test_message_edit_v1.py ]===== ##

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
def test_message_too_long(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_edit(user1['token'], response_data['message_id'], "A"*1500)
    assert message_response.status_code == 400

def test_invalid_fake_message_id(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']

    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_edit(user1['token'], response_data['message_id'] + 1, "Hey there")
    assert message_response.status_code == 400

def test_dm_message_too_long(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_edit(user1['token'], response_data['message_id'], "A"*1500)
    assert message_response.status_code == 400

def test_invalid_fake_message_id_2(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    message_id = response_data['message_id']
    assert message_response.status_code == 200
    assert message_id == 1

    message_response = rh.message_edit(user1['token'], message_id + 1, "Hey there")
    assert message_response.status_code == 400

def test_user_not_in_channel(clear, user1, user2, user3):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_edit(user3['token'], message_id, "Hello again.")
    assert message_response.status_code == 400

def test_user_not_in_dm(clear, user1, user2, user3):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']

    message_response = rh.message_senddm(user2['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_edit(user3['token'], message_id, "Hello again.")
    assert message_response.status_code == 400

def test_deleted_dm(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']

    message_response = rh.message_senddm(user2['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    rh.dm_remove(user1['token'], dm_id)

    edit_response = rh.message_edit(user2['token'], message_id, "Hello again.")
    assert edit_response.status_code == 400  

## Access Error - 403 ##
def test_unauthorised_user(clear, user1, user2, user3):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)
    rh.channel_join(user3['token'], channel_id)

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_edit(user3['token'], message_id, "Hello again.")
    assert message_response.status_code == 403

def test_user_not_owner(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)

    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_edit(user2['token'], message_id, "Hello again.")
    assert message_response.status_code == 403

def test_unauthorised_user_in_dm(clear, user1, user2, user3):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id'], user3['auth_user_id']]).json()['dm_id']
    message_response = rh.message_senddm(user2['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_edit(user3['token'], response_data['message_id'], "Hello again.")
    assert message_response.status_code == 403

# ==== Tests - Valids ==== #
def test_one_user_edits_one_message_in_one_channel(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_edit(user1['token'], message_id, "Hello again.")
    assert message_response.status_code == 200

def test_multiple_users_edits_multiple_messages_in_multiple_channels(clear, user1, user2):
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

    message_response = rh.message_edit(user1['token'], message_id1, "Hello again.")
    assert message_response.status_code == 200

    message_response = rh.message_edit(user1['token'], message_id2, "Hello again.")
    assert message_response.status_code == 200

    message_response = rh.message_edit(user2['token'], message_id3, "Hello again.")
    assert message_response.status_code == 200

    message_response = rh.message_edit(user2['token'], message_id4, "Hello again.")
    assert message_response.status_code == 200

    message_response = rh.message_edit(user1['token'], message_id5, "Hello again.")
    assert message_response.status_code == 200

    message_response = rh.message_edit(user1['token'], message_id6, "Hello again.")
    assert message_response.status_code == 200

    message_response = rh.message_edit(user2['token'], message_id7, "Hello again.")
    assert message_response.status_code == 200

    message_response = rh.message_edit(user2['token'], message_id8, "Hello again.")
    assert message_response.status_code == 200

def test_delete_message(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_edit(user1['token'], channel_id, "")
    assert message_response.status_code == 200

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

def test_owner_edits_another_users_message(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user2['token'], channel_id)

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_edit(user1['token'], message_id, "Hello again.")
    assert message_response.status_code == 200

def test_global_owner_edits_another_users_message(clear, user1, user2, user3):
    channel_id = rh.channels_create(user2['token'], "chan_name", True).json()['channel_id']
    rh.channel_join(user3['token'], channel_id)
    rh.channel_join(user1['token'], channel_id)

    message_response = rh.message_send(user1['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_edit(user1['token'], message_id, "Hello again.")
    assert message_response.status_code == 200

def test_one_user_invited_edits_one_messages_in_private_channel(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name2", False).json()['channel_id']
    rh.channel_invite(user1['token'], channel_id, user2['auth_user_id'])

    message_response = rh.message_send(user2['token'], channel_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1
    message_id = response_data['message_id']

    message_response = rh.message_edit(user2['token'], message_id, "Hello again.")
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

    message_response = rh.message_edit(user2['token'], message_id, "Hey")
    assert message_response.status_code == 200

def test_channel_messages_interaction(clear, user1):
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

    message_response = rh.message_edit(user1['token'], message_id2, "Woah")
    assert message_response.status_code == 200

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 2,
                "u_id": user1['auth_user_id'],
                "message": "Woah",
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

    message_response = rh.message_edit(user1['token'], message_id1, "Jeez")
    assert message_response.status_code == 200

    messages_response = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages_response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 2,
                "u_id": user1['auth_user_id'],
                "message": "Woah",
                "time_created": time_created2,
                "reacts": [],
                "is_pinned": False,
            }, 
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "Jeez",
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
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

def test_one_user_edits_one_message_in_dm(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    dm_message = rh.message_senddm(user1['token'], dm_id, "Hello")
    message_id = dm_message.json()['message_id']
    assert message_id == 1
    assert dm_message.status_code == 200
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

    dm_message = rh.message_edit(user1['token'], message_id, "Hey")
    assert dm_message.status_code == 200

    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = dm_messages.json()
    expected_result = {
        "messages": [
            {
                "message_id": message_id,
                "u_id": user1['auth_user_id'],
                "message": "Hey",
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

def test_delete_dm_message(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    dm_message = rh.message_senddm(user1['token'], dm_id, "Hello")
    message_id = dm_message.json()['message_id']
    assert message_id == 1
    assert dm_message.status_code == 200
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

    dm_message = rh.message_edit(user1['token'], message_id, "")
    assert dm_message.status_code == 200

    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = dm_messages.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

def test_owner_edits_another_users_dm_message(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    dm_message = rh.message_senddm(user2['token'], dm_id, "Hello")
    message_id = dm_message.json()['message_id']
    assert message_id == 1
    assert dm_message.status_code == 200
    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = dm_messages.json()
    expected_result = {
        "messages": [
            {
                "message_id": message_id,
                "u_id": user2['auth_user_id'],
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

    dm_message = rh.message_edit(user1['token'], message_id, "Hey")
    assert dm_message.status_code == 200

    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = dm_messages.json()
    expected_result = {
        "messages": [
            {
                "message_id": message_id,
                "u_id": user2['auth_user_id'],
                "message": "Hey",
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

    message = rh.message_edit(user1['token'], message_id, "Hey")
    assert message.status_code == 200

    messages = rh.channel_messages(user1['token'], channel_id, 0)
    response_data = messages.json()
    expected_result = {
        "messages": [
            {
                "message_id": message_id,
                "u_id": user1['auth_user_id'],
                "message": "Hey",
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

    dm_message = rh.message_edit(user1['token'], message_id, "Hey")
    assert dm_message.status_code == 200

    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    response_data = dm_messages.json()
    expected_result = {
        "messages": [
            {
                "message_id": message_id,
                "u_id": user3['auth_user_id'],
                "message": "Hey",
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