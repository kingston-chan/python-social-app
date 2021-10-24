import pytest
import requests
from src.config import url
import time
import json
from src.server import dm_create, dm_messages, message_senddm
import tests.route_helpers as rh

BASE_URL = url
## =====[ test_dm_messages_v1.py ]===== ##

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

# ==== Helper functions ==== #
def send_mass_dm_messages(user, messages_total, dm_id):
    message_list = []
    loop = 0
    while loop < messages_total:
        current_time = int(time.time())
        response_data = rh.message_senddm(user['token'], dm_id, "hello").json()
        message_id = response_data['message_id']
        message_dict = {
            "message_id":  message_id,
            "u_id": user['auth_user_id'],
            "message": "hello",
            "time_created": current_time
        }
        message_list.insert(0, message_dict)
        loop += 1
    return message_list

def make_mass_expected_results(start, end, messages_total, message_list):
    index = start
    counter = 0
    selected_messages = []
    while counter < 50 and index < messages_total:
        selected_message = message_list[index]
        message_dict = {
            "message_id": selected_message['message_id'],
            "u_id": selected_message['u_id'],
            "message": selected_message['message'],
            "time_created": selected_message['time_created']
        }
        selected_messages.append(message_dict)
        index += 1
        counter += 1

    if end == messages_total:
        end = -1

    return {
        "messages": selected_messages,
        "start": start,
        "end": end,
    }

# ==== Tests - Errors ==== #
def test_invalid_dm(clear, user1):
    # No channel created
    dm_messages_dict = {
        "token": user1['token'], 
        "dm_id": 1, 
        "start": 0,
    }
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params=dm_messages_dict)
    # Raise error
    assert response.status_code == 400

def test_incorrect_start(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    dm_messages_dict = {
        "token": user1['token'], 
        "dm_id": dm_id, 
        "start": 100,
    }
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params=dm_messages_dict)
    # Raise error
    assert response.status_code == 400

def test_invalid_member(clear, user1, user2, user3):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    dm_messages = rh.dm_messages(user3['token'], dm_id, 0)
    # Raise error
    assert dm_messages.status_code == 403

def test_invalid_member_2(clear, user1, user2, user3):
    dm_id1 = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    dm_id2 = rh.dm_create(user1['token'], [user3['auth_user_id']]).json()['dm_id']

    dm_messages = rh.dm_messages(user2['token'], dm_id2, 0)
    # Raise error
    assert dm_messages.status_code == 403

    dm_messages = rh.dm_messages(user3['token'], dm_id1, 0)
    # Raise error
    assert dm_messages.status_code == 403

def test_invalid_member_3(clear, user1, user2, user3, user4):
    dm_id1 = rh.dm_create(user2['token'], [user3['auth_user_id']]).json()['dm_id']
    dm_id2 = rh.dm_create(user2['token'], [user4['auth_user_id']]).json()['dm_id']

    dm_messages = rh.dm_messages(user4['token'], dm_id1, 0)
    assert dm_messages.status_code == 403 

    dm_messages = rh.dm_messages(user1['token'], dm_id1, 0)
    assert dm_messages.status_code == 403

    dm_messages = rh.dm_messages(user3['token'], dm_id2, 0)
    assert dm_messages.status_code == 403

    dm_messages = rh.dm_messages(user1['token'], dm_id2, 0)
    assert dm_messages.status_code == 403

# ==== Tests - Valids ==== #
def test_valid_dm_message(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
    assert dm_messages.status_code == 200
    response_data = dm_messages.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

def test_valid_dm_message_2(clear, user1, user2, user3):
    dm_id = rh.dm_create(user2['token'], [user3['auth_user_id']]).json()['dm_id']
    dm_messages = rh.dm_messages(user2['token'], dm_id, 0)
    assert dm_messages.status_code == 200
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert dm_messages.json() == expected_result

def test_multiple_channels(clear, user1, user2, user3, user4):
    dm_id1 = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    dm_id2 = rh.dm_create(user1['token'], [user3['auth_user_id']]).json()['dm_id']
    dm_id3 = rh.dm_create(user1['token'], [user4['auth_user_id']]).json()['dm_id']
    dm_id_list = [dm_id1, dm_id2, dm_id3]
    for dm_id in dm_id_list:
        dm_messages = rh.dm_messages(user1['token'], dm_id, 0)
        assert dm_messages.status_code == 200
        expected_result = {
            "messages": [],
            "start": 0,
            "end": -1,
        }
        assert dm_messages.json() == expected_result

def test_start_0_total_1(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    start = 0
    end = 1
    messages_total = 1
    
    message_list = send_mass_dm_messages(user1, messages_total, dm_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.dm_messages(user1['token'], dm_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_start_0_total_50(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    start = 0
    end = 50
    messages_total = 50
    
    message_list = send_mass_dm_messages(user1, messages_total, dm_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.dm_messages(user1['token'], dm_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_start_0_total_55(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    start = 0
    end = 50
    messages_total = 55
    
    message_list = send_mass_dm_messages(user1, messages_total, dm_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.dm_messages(user1['token'], dm_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_start_2_total_3(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    start = 2
    end = 3
    messages_total = 3
    
    message_list = send_mass_dm_messages(user1, messages_total, dm_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.dm_messages(user1['token'], dm_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_start_100_total_150(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    start = 100
    end = 150
    messages_total = 150
    
    message_list = send_mass_dm_messages(user1, messages_total, dm_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.dm_messages(user1['token'], dm_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_start_60_total_110(clear, user1, user2):
    dm_id = rh.dm_create(user1['token'], [user2['auth_user_id']]).json()['dm_id']
    start = 60
    end = 110
    messages_total = 110
    
    message_list = send_mass_dm_messages(user1, messages_total, dm_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.dm_messages(user1['token'], dm_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2
