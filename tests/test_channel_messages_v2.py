import pytest
import requests
from src.config import url
import datetime
import json

BASE_URL = url
# 403 - > access
# 400 - > input
# channel_messages_v1 tests

# test fixtures
@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")

@pytest.fixture
def user1():
    '''
    clear_v1()
    user = auth_register(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )
    return user['auth_user_id']
    '''
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
    '''
    user = auth_register(
        "fakeguytwo@fakeemail.com",
        "fakepasswordtwo",
        "fakefirstnametwo",
        "fakelastnametwo",
    )
    return user['auth_user_id']
    '''
    user_dict = {
        "email": "fakeguytwo@fakeemail.com",
        "password": "fakepasswordtwo",
        "name_first": "fakefirstnametwo",
        "name_last": "fakelastnametwo",
    }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_dict)
    return response.json()

def create_channel1(token):
    '''
    channel = channels_create(
        user,
        "random_channel_name1",
        True,
    )
    return channel
    '''
    channel_dict = {
        "token": token,
        "name": "random_channel_name1",
        "is_public": True,
    }
    payload = json.dumps(channel_dict)
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=payload)
    return response.json()

def create_channel2(token):
    '''
    channel = channels_create(
        user,
        "random_channel_name2",
        False,
    )
    return channel 
    '''
    channel_dict = {
        "token": token,
        "name": "random_channel_name2",
        "is_public": False,
    }
    payload = json.dumps(channel_dict)
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=payload)
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
# tests - errors
def test_ch_mess_error_channel_invalid(clear, user1):
    # no channel created
    # raise error
    # channel_messages_v1(user, 1, 0)
    messages_dict = {
        "token": user1['token'], 
        "channel_id": 2, 
        "start": 0, 
    }
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload)

    assert response.status_code == 400

def test_ch_mess_incorrect_start(clear, user1):
    channel = create_channel1(user1['token'])
    # raise error
    # channel_messages_v1(user, channel['channel_id'], 100)
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel['channel_id'], 
        "start": 100, 
    }
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload)
    assert response.status_code == 400

def test_ch_mess_error_member_invalid(clear, user1, user2):
    # raise error
    channel1 = create_channel1(user1['token'])
    # channel_messages_v1(user2, channel1['channel_id'], 0)
    messages_dict = {
        "token": user2['token'],
        "channel_id": channel1['channel_id'], 
        "start": 0,
    }
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload) 
    assert response.status_code == 403

def test_ch_mess_error_member_invalid2(clear, user1, user2):
    channel1 = create_channel1(user1['token'])
    channel2 = create_channel2(user2['token'])
    # raise errors
    # channel_messages_v1(user1, channel2['channel_id'], 0)
    messages_dict = {
        "token": user1['token'], 
        "channel_id": channel2['channel_id'], 
        "start": 0, 
    }        
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload) 
    assert response.status_code == 403

    messages_dict = {
        "token": user2['token'], 
        "channel_id": channel1['channel_id'], 
        "start": 0, 
    }        
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload)
    assert response.status_code == 403 

# test - valid scenarios
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
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload)
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
    # assert
    '''
    assert channel_messages_v1(user2, channel2['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }
    '''
    messages_dict = {
        "token": user2['token'], 
        "channel_id": channel2['channel_id'], 
        "start": 0, 
    }        
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.json() == expected_result

def test_ch_mess_multiple_channels(clear, user1):
    channel1 = create_channel1(user1['token'])
    channel2 = create_channel2(user1['token'])
    # assert
    '''
    assert channel_messages_v1(user1, channel1['channel_id'], 0) == {
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
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload)
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
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload)
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response.json() == expected_result


# future tests for future functions
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
    payload = json.dumps(messages_dict)
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=payload)
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