import pytest
import requests
from src.config import url
import datetime
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
    join_info = {
        "token": token,
        "channel_id": channel_id
    }
    requests.post(f"{BASE_URL}/channel/join/v2", json=join_info)

def invite_channel(token, channel_id, u_id):
    invite_info = {
        "token": token,
        "channel_id": channel_id,
        "u_id": u_id
    }
    requests.post(f"{BASE_URL}/channel/invite/v2", json=invite_info) 

# ==== Future functions ==== #
'''
def send_message(token, channel_id, message):
    message_dict = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
    }
    response = requests.post(f"{BASE_URL}/message/send/v1", json=message_dict)
    time = datetime.datetime.now()
    return response.json(), time
'''

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

# ==== Future Tests for Future Functions ==== #

def test_ch_mess_multiple_users_in_private_channel(clear, user1, user2):
    '''
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

    invite_channel(user1['token'], channel_id, user2['token'])

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
    '''
    pass

def test_ch_mess_1_message_in_channel(clear, user1):
    '''
    channel1 = create_channel1(user1['token'])
    
    send_message(user1['token'], channel1, "hello")
    current_time = datetime.datetime.now()

    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel1['channel_id'], 
        "start": 0, 
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    response_data = response.json()
    expected_result = {
        "messages": [
            {
                "message_id": 1,
                "u_id": user1['auth_user_id'],
                "message": "hello",
                "time_created": current_time
            }
        ],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result
    '''
    pass

def test_ch_mess_50_message_in_channel(clear, user1):
    pass

def test_ch_mess_55_message_in_channel(clear, user1):
    pass

def test_ch_mess_start_greater_than_1(clear, user1):
    pass
