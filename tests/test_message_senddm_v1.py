import pytest
import requests
from src.config import url
import time
import json
from src.server import dm_create, dm_messages, message_senddm
import tests.route_helpers as rh

BASE_URL = url
## =====[ test_message_senddm_v1.py ]===== ##

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

@pytest.fixture
def user4():
    return rh.auth_register("user4@email.com", "password", "user", "name").json()

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_invalid_dm(clear, user1, user2):
    dm_created = rh.dm_create(user1['token'], [user2['auth_user_id']])
    assert dm_created.status_code == 200
    dm_id = dm_created.json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id + 1, "Hello")
    assert message_response.status_code == 400

def test_message_too_long(clear, user1, user2):
    dm_created = rh.dm_create(user1['token'], [user2['auth_user_id']])
    assert dm_created.status_code == 200
    dm_id = dm_created.json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "A"*1500)
    assert message_response.status_code == 400

def test_message_too_short(clear, user1, user2):
    dm_created = rh.dm_create(user1['token'], [user2['auth_user_id']])
    assert dm_created.status_code == 200
    dm_id = dm_created.json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "")
    assert message_response.status_code == 400

## Access Error - 403 ##
def test_real_unauthorised_user(clear, user1, user2, user3):
    dm_created = rh.dm_create(user1['token'], [user2['auth_user_id']])
    assert dm_created.status_code == 200
    dm_id = dm_created.json()['dm_id']
    message_response = rh.message_senddm(user3['token'], dm_id, "Hello")
    assert message_response.status_code == 403

def test_real_unauthorised_user2(clear, user1, user2, user3, user4):
    dm_created = rh.dm_create(user2['token'], [user3['auth_user_id']])
    assert dm_created.status_code == 200
    dm_id = dm_created.json()['dm_id']
    message_response = rh.message_senddm(user4['token'], dm_id, "Hello")
    assert message_response.status_code == 403

def test_real_unauthorised_user3(clear, user1, user2, user3, user4):
    dm_created = rh.dm_create(user2['token'], [user3['auth_user_id'], user4['auth_user_id']])
    assert dm_created.status_code == 200
    dm_id = dm_created.json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    assert message_response.status_code == 403

def test_dummy_unauthorised_user(clear, user1, user2):
    dm_created = rh.dm_create(user1['token'], [user1['auth_user_id'], user2['auth_user_id']])
    assert dm_created.status_code == 200
    dm_id = dm_created.json()['dm_id']
    message_response = rh.message_senddm(9999, dm_id, "Hello")
    assert message_response.status_code == 403

# ==== Tests - Valids ==== #
def test_one_user_sends_one_message_in_one_dm(clear, user1, user2):
    dm_created = rh.dm_create(user1['token'], [user2['auth_user_id']])
    assert dm_created.status_code == 200
    dm_id = dm_created.json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

def test_multiple_users_sends_multiple_messages_in_multiple_dms(clear, user1, user2, user3):
    dm_created1 = rh.dm_create(user1['token'], [user2['auth_user_id']])
    dm_created2 = rh.dm_create(user1['token'], [user3['auth_user_id']])
    assert dm_created1.status_code == 200
    dm_id1 = dm_created1.json()['dm_id']
    assert dm_created2.status_code == 200
    dm_id2 = dm_created2.json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id1, "One")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    message_response = rh.message_senddm(user1['token'], dm_id1, "Two")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 2

    message_response = rh.message_senddm(user2['token'], dm_id1, "Three")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 3

    message_response = rh.message_senddm(user2['token'], dm_id1, "Four")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 4

    message_response = rh.message_senddm(user1['token'], dm_id2, "Five")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 5

    message_response = rh.message_senddm(user1['token'], dm_id2, "Six")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 6

    message_response = rh.message_senddm(user3['token'], dm_id2, "Seven")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 7

    message_response = rh.message_senddm(user3['token'], dm_id2, "Eight")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 8

def test_dm_messages_interaction(clear, user1, user2):
    dm_created = rh.dm_create(user1['token'], [user2['auth_user_id']])
    assert dm_created.status_code == 200
    dm_id = dm_created.json()['dm_id']
    message_response = rh.message_senddm(user1['token'], dm_id, "Hello")
    response_data = message_response.json()
    assert message_response.status_code == 200
    assert response_data['message_id'] == 1

    messages_response = rh.dm_messages(user1['token'], dm_id, 0)
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