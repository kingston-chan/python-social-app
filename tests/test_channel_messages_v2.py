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
        "email": "fakeguy@fakeemail.com",
        "password": "fakepassword",
        "name_first": "fakefirstname",
        "name_last": "fakelastname",
    }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_dict) 
    return response.json()

@pytest.fixture
def user2():
    user_dict = {
        "email": "fakeguytwo@fakeemail.com",
        "password": "fakepasswordtwo",
        "name_first": "fakefirstnametwo",
        "name_last": "fakelastnametwo",
    }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_dict)
    return response.json()

# ==== Helper functions ==== #
def create_channel1(token):
    channel_dict = {
        "token": token,
        "name": "random_channel_name1",
        "is_public": True,
    }
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_dict)
    return response.json()

def create_channel2(token):
    channel_dict = {
        "token": token,
        "name": "random_channel_name2",
        "is_public": False,
    }
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_dict)
    return response.json()
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
def test_ch_mess_error_invalid_channnel(clear, user1):
    # No channel created
    messages_dict = {
        "token": user1['token'], 
        "channel_id": 2, 
        "start": 0, 
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    # Raise error
    assert response.status_code == 400

def test_ch_mess_incorrect_start(clear, user1):
    channel = create_channel1(user1['token'])
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel['channel_id'], 
        "start": 100, 
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    # Raise error
    assert response.status_code == 400

def test_ch_mess_error_invalid_member(clear, user1, user2):
    channel1 = create_channel1(user1['token'])
    messages_dict = {
        "token": user2['token'],
        "channel_id": channel1['channel_id'], 
        "start": 0,
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict) 
    # Raise error
    assert response.status_code == 403

def test_ch_mess_error_invalid_member2(clear, user1, user2):
    channel1 = create_channel1(user1['token'])
    channel2 = create_channel2(user2['token'])
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel2['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict) 
    # Raise error
    assert response.status_code == 403

    messages_dict = {
        "token": user2['token'], 
        "channel_id": channel1['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    
    assert response.status_code == 403 

# ==== Tests - Valids ==== #
def test_ch_mess_public_channel(clear, user1):
    channel1 = create_channel1(user1['token'])
    # assert
    '''
    assert channel_messages(user1, channel1['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }
    '''
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel1['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    assert response.status_code == 200
    response_data = response.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

def test_ch_mess_private_channel(clear, user2):
    channel2 = create_channel2(user2['token'])
    messages_dict = {
        "token": user2['token'], 
        "channel_id": channel2['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.json() == expected_result

def test_ch_mess_multiple_channels(clear, user1):
    channel1 = create_channel1(user1['token'])
    channel2 = create_channel2(user1['token'])
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel1['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.json() == expected_result

    '''
    assert channel_messages_v1(user1, channel2['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }
    '''
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel2['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.json() == expected_result


# ==== Future Tests for Future Functions ==== #
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