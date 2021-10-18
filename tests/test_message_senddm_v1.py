import pytest
import requests
from src.config import url
import time
import json

BASE_URL = url
## =====[ test_message_senddm_v1.py ]===== ##

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

@pytest.fixture
def user3():
    user_dict = {
        "email": "user3@email.com",
        "password": "password",
        "name_first": "user",
        "name_last": "name"
    }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_dict)
    return response.json()

# ==== Helper functions ==== #
def create_dm(token, u_ids):
    channel_info = {
        "token": token, 
        "u_ids": u_ids
    }
    response = requests.post(f"{BASE_URL}/dm/create/v1", json=channel_info)
    response_data = response.json()
    return int(response_data['dm_id'])

def print_dm_messages(token, dm_id, start):
    dm_messages_info = {
        "token": token,
        "dm_id": dm_id,
        "start": start 
    }
    return requests.get(f"{BASE_URL}/dm/messages/v1", params=dm_messages_info)

def send_dm_message(token, dm_id, message):
    dm_message_info = {
        "token": token,
        "dm_id": dm_id,
        "message": message
    }
    return requests.post(f"{BASE_URL}/message/senddm/v1", json=dm_message_info)

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_invalid_dm(clear, user1, user2):
    dm_id = create_dm(user1['token'], [user1['auth_user_id'], user2['auth_user_id']])
    message_response = send_dm_message(user1['token'], dm_id + 1, "Hello")
    assert message_response.status_code == 400

def test_message_too_long(clear, user1, user2):
    dm_id = create_dm(user1['token'], [user1['auth_user_id'], user2['auth_user_id']])
    message_response = send_dm_message(user1['token'], dm_id, "A"*1500)
    assert message_response.status_code == 400

def test_message_too_short(clear, user1, user2):
    dm_id = create_dm(user1['token'], [user1['auth_user_id'], user2['auth_user_id']])
    message_response = send_dm_message(user1['token'], dm_id, "")
    assert message_response.status_code == 400

## Access Error - 403 ##
def test_real_unauthorised_user(clear, user1, user2, user3):
    dm_id = create_dm(user1['token'], [user1['auth_user_id'], user2['auth_user_id']])
    message_response = send_dm_message(user3['token'], dm_id, "Hello")
    assert message_response.status_code == 403

def test_real_unauthorised_user2(clear, user1, user2, user3, user4):
    dm_id = create_dm(user2['token'], [user2['auth_user_id'], user3['auth_user_id']])
    message_response = send_dm_message(user4['token'], dm_id, "Hello")
    assert message_response.status_code == 403

def test_real_unauthorised_user3(clear, user1, user2, user3):
    dm_id = create_dm(user2['token'], [user2['auth_user_id'], user3['auth_user_id']])
    message_response = send_dm_message(user1['token'], dm_id, "Hello")
    assert message_response.status_code == 403

def test_dummy_unauthorised_user(clear, user1, user2):
    dm_id = create_dm(user1['token'], [user1['auth_user_id'], user2['auth_user_id']])
    message_response = send_dm_message(9999, dm_id, "Hello")
    assert message_response.status_code == 403

# ==== Tests - Valids ==== #
def test_one_user_sends_one_message_in_one_dm(clear, user1, user2):
    dm_id = create_dm(user1['token'], [user1['auth_user_id'], user2['auth_user_id']])
    message_response = send_dm_message(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

def test_multiple_users_sends_multiple_messages_in_multiple_dms(clear, user1, user2, user3):
    dm_id1 = create_dm(user1['token'], [user1['auth_user_id'], user2['auth_user_id']])
    dm_id2 = create_dm(user1['token'], [user1['auth_user_id'], user3['auth_user_id']])

    message_response = send_dm_message(user1['token'], dm_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = send_dm_message(user1['token'], dm_id1, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = send_dm_message(user2['token'], dm_id1, "Three")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 3

    message_response = send_dm_message(user2['token'], dm_id1, "Four")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 4

    message_response = send_dm_message(user1['token'], dm_id2, "Five")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 5

    message_response = send_dm_message(user1['token'], dm_id2, "Six")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 6

    message_response = send_dm_message(user3['token'], dm_id2, "Seven")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 7

    message_response = send_dm_message(user3['token'], dm_id2, "Eight")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 8

def test_dm_messages_interaction(clear, user1, user2):
    dm_id = create_dm(user1['token'], [user1['auth_user_id'], user2['auth_user_id']])

    message_response = send_dm_message(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    messages_response = print_dm_messages(user1['token'], dm_id, 0)
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
