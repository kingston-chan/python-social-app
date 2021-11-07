import pytest
import requests
from src.config import url
import time
import json
import tests.route_helpers as rh

BASE_URL = url
## =====[ test_channel_messages_v2.py ]===== ##

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

# ==== Helper functions ==== #
def send_mass_messages(user, messages_total, channel_id):
    message_list = []
    loop = 0
    while loop < messages_total:
        current_time = int(time.time())
        response_data = rh.message_send(user['token'], channel_id, "hello").json()
        message_id = response_data['message_id']
        message_dict = {
            "message_id":  message_id,
            "u_id": user['auth_user_id'],
            "message": "hello",
            "time_created": current_time,
            "reacts": [],
            "is_pinned": False,
        }
        message_list.insert(0, message_dict)
        loop += 1
    return message_list

def make_mass_expected_results(start, end, messages_total, message_list):
    index = start
    counter = 0
    selected_messages = []
    while counter < 50 and index < messages_total:
        selected_messages.append(message_list[index])
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
def test_ch_mess_error_invalid_channel(clear, user1):
    # No channel created
    messages_dict = {
        "token": user1['token'], 
        "channel_id": 1, 
        "start": 0,
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    # Raise error
    assert response.status_code == 400

def test_ch_mess_incorrect_start(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel_id, 
        "start": 100,
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    # Raise error
    assert response.status_code == 400

def test_ch_mess_error_invalid_member(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    messages_dict = {
        "token": user2['token'],
        "channel_id": channel_id, 
        "start": 0
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict) 
    # Raise error
    assert response.status_code == 403

def test_ch_mess_error_invalid_member2(clear, user1, user2):
    channel_id1 = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    channel_id2 = rh.channels_create(user2['token'], "chan_name2", True).json()['channel_id']
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel_id2, 
        "start": 0
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict) 
    # Raise error
    assert response.status_code == 403

    messages_dict = {
        "token": user2['token'], 
        "channel_id": channel_id1, 
        "start": 0
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    
    assert response.status_code == 403 

# ==== Tests - Valids ==== #
def test_ch_mess_public_channel(clear, user1):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel_id, 
        "start": 0
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    assert response.status_code == 200
    response_data = response.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

def test_ch_mess_private_channel(clear, user2):
    channel_id = rh.channels_create(user2['token'], "chan_name", False).json()['channel_id']
    messages_dict = {
        "token": user2['token'], 
        "channel_id": channel_id, 
        "start": 0
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.json() == expected_result

def test_ch_mess_multiple_channels(clear, user1):
    channel_id1 = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    channel_id2 = rh.channels_create(user1['token'], "chan_name2", False).json()['channel_id']
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel_id1, 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.json() == expected_result

    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel_id2, 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.json() == expected_result

def test_ch_mess_multiple_users_in_public_channel(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", True).json()['channel_id']
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel_id, 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.status_code == 200
    assert response.json() == expected_result

    rh.channel_join(user2['token'], channel_id)

    messages_dict = {
        "token": user2['token'], 
        "channel_id": channel_id, 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.status_code == 200
    assert response.json() == expected_result

def test_ch_mess_multiple_users_in_private_channel(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "chan_name", False).json()['channel_id']
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel_id, 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.status_code == 200
    assert response.json() == expected_result

    rh.channel_invite(user1['token'], channel_id, user2['auth_user_id'])

    messages_dict = {
        "token": user2['token'], 
        "channel_id": channel_id, 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.status_code == 200
    assert response.json() == expected_result

def test_ch_mess_start_0_total_1(clear, user1):
    channel_id = rh.channels_create(user1['token'], "channel_name", True).json()['channel_id']
    start = 0
    end = 1
    messages_total = 1
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

def test_ch_mess_start_0_total_50(clear, user1):
    channel_id = rh.channels_create(user1['token'], "channel_name", True).json()['channel_id']
    start = 0
    end = 50
    messages_total = 50
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

def test_ch_mess_start_0_total_55(clear, user1):
    channel_id = rh.channels_create(user1['token'], "channel_name", True).json()['channel_id']
    start = 0
    end = 50
    messages_total = 55
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

def test_ch_mess_start_2_total_3(clear, user1):
    channel_id = rh.channels_create(user1['token'], "channel_name", True).json()['channel_id']
    start = 2
    end = 3
    messages_total = 3
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

def test_ch_mess_start_100_total_150(clear, user1):
    channel_id = rh.channels_create(user1['token'], "channel_name", True).json()['channel_id']
    start = 100
    end = 150
    messages_total = 150
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

def test_ch_mess_start_60_total_110(clear, user1):
    channel_id = rh.channels_create(user1['token'], "channel_name", True).json()['channel_id']
    start = 60
    end = 110
    messages_total = 110
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = rh.channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2
        assert response_data['messages'][x]['reacts'] == expected_result['messages'][x]['reacts']
        assert response_data['messages'][x]['is_pinned'] == expected_result['messages'][x]['is_pinned']

def test_ch_mess_shows_correct_reacts(clear, user1, user2):
    channel_id = rh.channels_create(user1['token'], "channel_name", True).json()['channel_id']
    rh.channel_join(user2["token"], channel_id)
    
    rh.message_send(user1['token'], channel_id, "hello").json()["message_id"]
    msg2 = rh.message_send(user1['token'], channel_id, "hello").json()["message_id"]
    rh.message_send(user1['token'], channel_id, "hello").json()["message_id"]
    msg4 = rh.message_send(user1['token'], channel_id, "hello").json()["message_id"]

    react_id = 1
    
    rh.message_react(user1['token'], msg2, react_id)
    rh.message_react(user1['token'], msg4, react_id)

    messages_user1 = rh.channel_messages(user1['token'], channel_id, 0).json()["messages"]

    # Test that reacts and each react is correct type
    assert type(messages_user1[0]["reacts"]) is list
    assert type(messages_user1[0]["reacts"][0]) is dict
    assert len(messages_user1[0]["reacts"]) == 1

    # Test react contains corret keys
    assert "react_id" in messages_user1[0]["reacts"][0]
    assert "u_ids" in messages_user1[0]["reacts"][0]
    assert "is_this_user_reacted" in messages_user1[0]["reacts"][0]

    # Test values of react
    assert messages_user1[0]["reacts"][0]["react_id"] == react_id
    # Test u_ids is a list
    assert type(messages_user1[0]["reacts"][0]["u_ids"]) is list
    assert user1["auth_user_id"] in messages_user1[0]["reacts"][0]["u_ids"]
    assert messages_user1[0]["reacts"][0]["is_this_user_reacted"] == True

    assert len(messages_user1[2]["reacts"]) == 1
    assert messages_user1[2]["reacts"][0]["react_id"] == react_id
    assert user1["auth_user_id"] in messages_user1[2]["reacts"][0]["u_ids"]
    assert messages_user1[0]["reacts"][0]["is_this_user_reacted"] == True
    
    # No reactions so empty
    assert messages_user1[1]["reacts"] == []
    assert messages_user1[3]["reacts"] == []

    # Test values of react for user not reacted, but someone has
    messages_user2 = rh.channel_messages(user2['token'], channel_id, 0).json()["messages"]

    assert messages_user2[0]["reacts"][0]["react_id"] == react_id
    assert user2["auth_user_id"] not in messages_user2[0]["reacts"][0]["u_ids"]
    assert messages_user2[0]["reacts"][0]["is_this_user_reacted"] == False

    assert messages_user2[2]["reacts"][0]["react_id"] == react_id
    assert user2["auth_user_id"] not in messages_user2[2]["reacts"][0]["u_ids"]
    assert messages_user2[2]["reacts"][0]["is_this_user_reacted"] == False