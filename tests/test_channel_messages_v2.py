import pytest
import requests
from src.config import url
from src.error import InputError, AccessError

BASE_URL = url
# 403 - > access
# 400 - > input
# channel_messages_v1 tests

# test fixtures
@pytest.fixture
def clear():
    response = requests.delete(f"{BASE_URL}/clear/v1")

@pytest.fixture
def create_user1():
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
def create_user2():
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
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_dict)
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
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_dict)
    return response.json()

def send_message(token, channel_id, message):
    message_dict = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
    }
    response = requests.post(f"{BASE_URL}/message/send/v1", json=message_dict)
    return response.json()


# tests - errors
def test_ch_mess_error_channel_invalid(clear, create_user1):
    # no channel created
    # raise error
    with pytest.raises(InputError):
        # channel_messages_v1(user, 1, 0)
        messages_dict = {
            "token": create_user1, 
            "channel_id": 1, 
            "start": 0, 
        }
        requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)

def test_ch_mess_incorrect_start(clear, create_user1):
    channel = create_channel1(create_user1['token'])
    # raise error
    # channel_messages_v1(user, channel['channel_id'], 100)
    messages_dict = {
        "token": create_user1['token'], 
        "channel_id": channel['channel_id'], 
        "start": 100, 
    }
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)

    assert response.status_code == 400

def test_ch_mess_error_member_invalid(clear_and_create_user1, create_user2):
    # raise error
    token1 = clear_and_create_user1
    token2 = create_user2
    channel1 = create_channel1(token1)
    with pytest.raises(AccessError):
        # channel_messages_v1(user2, channel1['channel_id'], 0)
        messages_dict = {
            "token": token2, 
            "channel_id": channel1['channel_id'], 
            "start": 0, 
        }
        response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict) 

        assert response.status_code == 403 

def test_ch_mess_error_member_invalid2(clear_and_create_user1, create_user2):
    token1 = clear_and_create_user1
    token2 = create_user2
    channel1 = create_channel1(token1)
    channel2 = create_channel2(token2)
    # raise errors
    with pytest.raises(AccessError):
        # channel_messages_v1(user1, channel2['channel_id'], 0)
        messages_dict = {
            "token": token1, 
            "channel_id": channel2['channel_id'], 
            "start": 0, 
        }        
        requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict) 

    with pytest.raises(AccessError):
        # channel_messages_v1(user2, channel1['channel_id'], 0)
        messages_dict = {
            "token": token2, 
            "channel_id": channel1['channel_id'], 
            "start": 0, 
        }        
        requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict) 

# test - valid scenarios
def test_ch_mess_public_channel(clear_and_create_user1):
    token1 = clear_and_create_user1
    channel1 = create_channel1(token1)
    # assert
    '''
    assert channel_messages(user1, channel1['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }
    '''
    messages_dict = {
        "token": clear_and_create_user1, 
        "channel_id": channel1['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    response_data = response.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

def test_ch_mess_private_channel(clear_and_create_user1, create_user2):
    token1 = clear_and_create_user1
    token2 = create_user2
    create_channel1(token1)
    channel2 = create_channel2(token2)
    # assert
    '''
    assert channel_messages_v1(user2, channel2['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }
    '''
    messages_dict = {
        "token": token2, 
        "channel_id": channel2['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    response_data = response.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

def test_ch_mess_multiple_channels(clear_and_create_user1):
    token1 = clear_and_create_user1
    channel1 = create_channel1(token1)
    channel2 = create_channel2(token1)

    # assert
    '''
    assert channel_messages_v1(user1, channel1['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }
    '''
    messages_dict = {
        "token": token1, 
        "channel_id": channel1['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    response_data = response.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

    '''
    assert channel_messages_v1(user1, channel2['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }
    '''
    messages_dict = {
        "token": token1, 
        "channel_id": channel2['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    response_data = response.json()
    expected_result = {
        "messages": [],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result

def test_ch_mess_1_message_in_channel(clear_and_create_user1):
    token1 = clear_and_create_user1
    channel1 = create_channel1(token1)
    
    send_message(token1, channel1, "hello")

    messages_dict = {
        "token": token1, 
        "channel_id": channel1['channel_id'], 
        "start": 0, 
    }        
    response = requests.get(f"{BASE_URL}/channel/messages/v2", json=messages_dict)
    response_data = response.json()
    expected_result = {
        "messages": [

        ],
        "start": 0,
        "end": -1,
    }
    assert response_data == expected_result