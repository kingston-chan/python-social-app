import pytest
import requests
from src.config import url
import time
import json

BASE_URL = url
## =====[ test_channel_messages_v2.py ]===== ##

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

def print_channel_messages(token, channel_id, start):
    messages_info = {
        "token": token,
        "channel_id": channel_id,
        "start": start 
    }
    return requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_info)

def send_mass_messages(user, messages_total, channel_id):
    message_list = []
    loop = 0
    while loop < messages_total:
        current_time = int(time.time())
        response_data = send_message(user['token'], channel_id, "hello").json()
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
    channel_id = create_channel(user1['token'], "chan_name", True)
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel_id, 
        "start": 100,
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict)
    # Raise error
    assert response.status_code == 400

def test_ch_mess_error_invalid_member(clear, user1, user2):
    channel_id = create_channel(user1['token'], "chan_name", True)
    messages_dict = {
        "token": user2['token'],
        "channel_id": channel_id, 
        "start": 0
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params=messages_dict) 
    # Raise error
    assert response.status_code == 403

def test_ch_mess_error_invalid_member2(clear, user1, user2):
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    channel_id2 = create_channel(user2['token'], "chan_name2", True)
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
    channel_id = create_channel(user1['token'], "chan_name", True)
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
    channel_id = create_channel(user2['token'], "chan_name", False)
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
    channel_id1 = create_channel(user1['token'], "chan_name", True)
    channel_id2 = create_channel(user1['token'], "chan_name2", False)
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
    channel_id = create_channel(user1['token'], "chan_name", True)
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

    join_channel(user2['token'], channel_id)

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
    channel_id = create_channel(user1['token'], "chan_name", False)
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

    invite_member_to_channel(user1['token'], channel_id, user2['auth_user_id'])

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
    channel_id = create_channel(user1['token'], "channel_name", True)
    start = 0
    end = 1
    messages_total = 1
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = print_channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_ch_mess_start_0_total_50(clear, user1):
    channel_id = create_channel(user1['token'], "channel_name", True)
    start = 0
    end = 50
    messages_total = 50
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = print_channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_ch_mess_start_0_total_55(clear, user1):
    channel_id = create_channel(user1['token'], "channel_name", True)
    start = 0
    end = 50
    messages_total = 55
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = print_channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_ch_mess_start_2_total_3(clear, user1):
    channel_id = create_channel(user1['token'], "channel_name", True)
    start = 2
    end = 3
    messages_total = 3
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = print_channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_ch_mess_start_100_total_150(clear, user1):
    channel_id = create_channel(user1['token'], "channel_name", True)
    start = 100
    end = 150
    messages_total = 150
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = print_channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2

def test_ch_mess_start_60_total_110(clear, user1):
    channel_id = create_channel(user1['token'], "channel_name", True)
    start = 60
    end = 110
    messages_total = 110
    
    message_list = send_mass_messages(user1, messages_total, channel_id)
    expected_result = make_mass_expected_results(start, end, messages_total, message_list)
    response_data = print_channel_messages(user1['token'], channel_id, start).json()

    assert response_data['start'] == expected_result['start']
    assert response_data['end'] == expected_result['end']
    for x in range(len(response_data['messages'])):
        print(f"message:={x}")
        assert response_data['messages'][x]['message_id'] == expected_result['messages'][x]['message_id']
        assert response_data['messages'][x]['u_id'] == expected_result['messages'][x]['u_id']
        assert response_data['messages'][x]['message'] == expected_result['messages'][x]['message']
        assert abs(response_data['messages'][x]['time_created'] - expected_result['messages'][x]['time_created']) < 2