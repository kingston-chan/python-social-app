import json
import requests
import pytest
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

#400 is input error
#403 is access error

#==Fixtures==#

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")
@pytest.fixture
def user1():
    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user)
    return response.json()
@pytest.fixture
def user2():
    new_user1 = {"email" : "fakeguy1@gmail.com" , "password": "fake123451","name_first" : "faker", "name_last" : "is_a_faker1" }   
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user1)
    return response.json()

#==Helper Functions==#

def dm_list(token):
    list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : token })
    return list_of_dicts.json()
def dm_create(token, u_ids):
    response = requests.post(f"{url}/dm/create/v1", json={"token" : token , "u_ids" : u_ids})
    dm_id = response.json()
    return dm_id
def channel_create_public(user):
    response = requests.post(f"{url}/channel/create/v1", json={"token" : user["token"]})
    channel_id = response.json()
    return channel_id

#==tests==#

def test_invalid_token(clear):
    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : 0, "message_id": 'a', "react_id" : 'a'})
    assert response.status_code == 403

def test_unauthorised_token_for_dm(clear,user1,user2):
    new_user_token = user1["token"]
    unauth_token = user2["token"]

    dm_create(new_user_token,[])

    dm_messages_dict = {"token": user1['token'], "dm_id": 1, "message": "This assignment is too long"}
    message_id = requests.post(f"{BASE_URL}/message/senddm/v1", json=dm_messages_dict)

    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : unauth_token, "message_id": message_id, "react_id" : 2})

    assert response.status_code == 400 

def test_unauthorised_token_for_channel(clear,user1,user2):
    
    unauth_token = user2["token"]

    channel_id = channel_create_public(user1)

    channel_messages_dict = {"token": user1['token'], "channel_id": channel_id, "message": "This assignment is too long"}
    message_id = requests.post(f"{BASE_URL}/message/send/v1", json=channel_messages_dict)

    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : unauth_token, "message_id": message_id, "react_id" : 1})

    assert response.status_code == 400 

def test_invalid_react_id(clear,user1):
        
    auth_token = user1["token"]

    channel_id = channel_create_public(user1)

    channel_messages_dict = {"token": user1['token'], "channel_id": channel_id, "message": "This assignment is too long"}

    message_id = requests.post(f"{BASE_URL}/message/send/v1", json=channel_messages_dict)

    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : auth_token, "message_id": message_id, "react_id" : 2})

    assert response.status_code == 400 

def test_invalid_message_id(clear,user1):
            
    auth_token = user1["token"]

    channel_id = channel_create_public(user1)

    channel_messages_dict = {"token": user1['token'], "channel_id": channel_id, "message": "This assignment is too long"}
    response = requests.get(f"{BASE_URL}/messages/send/v2", json=channel_messages_dict)
    message_id = response.json()["message_id"] + 1
    
    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : auth_token, "message_id": message_id, "react_id" : 1})

    assert response.status_code == 400 
'''
def test_seccessful_case_dm_react():
    return None 
def test_seccessful_case_channel_react():
    return None 
'''