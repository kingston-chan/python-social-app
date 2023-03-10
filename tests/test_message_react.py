import pytest, requests
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
def dm_create(token, u_ids):
    response = requests.post(f"{url}/dm/create/v1", json={"token" : token , "u_ids" : u_ids})
    dm_id = response.json()
    return dm_id["dm_id"]
def channel_create_public(token):
    response = requests.post(f"{url}/channels/create/v2", json={"token" : token , "name" : "fake_guys_channel" , "is_public": True })
    channel_id = response.json()
    return channel_id["channel_id"]

#==tests==#
def test_invalid_token(clear):
    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : 0, "message_id": 'a', "react_id" : 1})
    assert response.status_code == 403

def test_unauthorised_token_for_dm(clear,user1,user2):
    new_user_token = user1["token"]
    unauth_token = user2["token"]

    dm_create(new_user_token,[])

    dm_messages_dict = {"token": user1['token'], "dm_id": 1, "message": "This assignment is too long"}
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json=dm_messages_dict)
    message_id = response.json()["message_id"]

    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : unauth_token, "message_id": message_id, "react_id" : 1})

    assert response.status_code == 400 

def test_unauthorised_token_for_channel(clear,user1,user2):
    
    unauth_token = user2["token"]

    channel_id = channel_create_public(user1["token"])

    channel_messages_dict = {"token": user1['token'], "channel_id": channel_id, "message": "This assignment is too long"}
    response = requests.post(f"{BASE_URL}/message/send/v1", json=channel_messages_dict)
    message_id = response.json()["message_id"]

    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : unauth_token, "message_id": message_id, "react_id" : 1})

    assert response.status_code == 400 

def test_invalid_react_id(clear,user1):
        
    auth_token = user1["token"]

    channel_id = channel_create_public(user1["token"])

    channel_messages_dict = {"token": user1['token'], "channel_id": channel_id, "message": "This assignment is too long"}

    response = requests.post(f"{BASE_URL}/message/send/v1", json=channel_messages_dict)
    message_id = response.json()["message_id"]

    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : auth_token, "message_id": message_id, "react_id" : 2})

    assert response.status_code == 400 

def test_invalid_message_id(clear,user1):
            
    auth_token = user1["token"]
    
    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : auth_token, "message_id": 'a', "react_id" : 1})

    assert response.status_code == 400 

def test_already_reacted_for_dm(clear,user1):
    new_user_token = user1["token"]

    dm_create(new_user_token,[])

    dm_messages_dict = {"token": user1['token'], "dm_id": 1, "message": "This assignment is too long"}
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json=dm_messages_dict)
    message_id = response.json()["message_id"]

    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : new_user_token, "message_id": message_id, "react_id" : 1})
    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : new_user_token, "message_id": message_id, "react_id" : 1})

    assert response.status_code == 400 

def test_already_reacted_for_channel(clear,user1):
    new_user_token = user1["token"]

    channel_id = channel_create_public(user1["token"])

    channel_messages_dict = {"token": user1['token'], "channel_id": channel_id, "message": "This assignment is too long"}

    response = requests.post(f"{BASE_URL}/message/send/v1", json=channel_messages_dict)
    message_id = response.json()["message_id"]

    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : new_user_token, "message_id": message_id, "react_id" : 1})
    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : new_user_token, "message_id": message_id, "react_id" : 1})

    assert response.status_code == 400

def test_multiple_users_react(clear, user1, user2):
    channel_1 = rh.channels_create(user1["token"], "channel1", True).json()["channel_id"]
    dm_1 = rh.dm_create(user1["token"], [user2["auth_user_id"]]).json()["dm_id"]
    rh.channel_join(user2["token"], channel_1)

    channel_msg = rh.message_send(user1["token"], channel_1, "hello").json()["message_id"]
    dm_msg = rh.message_senddm(user1["token"], dm_1, "hello").json()["message_id"]

    rh.message_react(user1["token"], channel_msg, 1)
    rh.message_react(user1["token"], dm_msg, 1)

    assert rh.message_react(user2["token"], channel_msg, 1).status_code == 200
    assert rh.message_react(user2["token"], dm_msg, 1).status_code == 200