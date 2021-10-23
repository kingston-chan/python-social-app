import requests
import tests.route_helpers as rh
from src.config import url
import pytest

BASE_URL = url
#400 is input error
#403 is access error
#==Fixtures==#
@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")
@pytest.fixture
def user1():
    response = rh.auth_register("fakeguy@gmail.com","fake12345","faker","is_a_faker")
    return response.json()
@pytest.fixture
def user2():
    response = rh.auth_register("fakeguy1@gmail.com","fake123451","faker","is_a_faker1")
    return response.json()
@pytest.fixture
def user3():   
    response = rh.auth_register("fakeguy2@gmail.com","fake123452","faker","is_a_faker2")
    return response.json()
#==test==#
def test_invalid_channel(clear,user1,user2):
    auth_user_token = user1["token"]

    response = rh.channels_create(auth_user_token,"fakeguy",True)
    response_data = response.json()

    invalid_channel_id = response_data["channel_id"] + 1

    new_user_id = user2["auth_user_id"]

    #response = requests.post(f"{url}/channel/invite/v2", json={"token": auth_user_token, "channel_id": invalid_channel_id, "u_id" : new_user_id})
    response = rh.channel_invite(auth_user_token,invalid_channel_id,new_user_id)
    assert response.status_code == 400

def test_already_member(clear, user1):
    auth_user_token = user1["token"]
    new_user_id = user1["auth_user_id"]

    response = rh.channels_create(auth_user_token,"fakeguy",True)
    response_data = response.json()

    channel_id = response_data["channel_id"]

    #response = requests.post(f"{url}/channel/invite/v2", json={"token": auth_user_token, "channel_id": channel_id, "u_id" : new_user_id})
    response = rh.channel_invite(auth_user_token,channel_id,new_user_id)
    assert response.status_code == 400

def test_invalid_user_id(clear, user1):
    auth_user_token = user1["token"]
    new_user_id = user1["auth_user_id"]

    response = rh.channels_create(auth_user_token,"fakeguy",True)
    response_data = response.json()

    channel_id = response_data["channel_id"]

    invalid_u_id = new_user_id + 1

    #response = requests.post(f"{url}/channel/invite/v2", json={"token": auth_user_token, "channel_id": channel_id, "u_id" : invalid_u_id})
    response = rh.channel_invite(auth_user_token,channel_id,invalid_u_id)
    assert response.status_code == 400

def test_not_auth_user(clear,user1,user2,user3):
    auth_user_token = user1["token"]
    
    response = rh.channels_create(auth_user_token,"fakeguy",True)

    response_data = response.json()

    channel_id = response_data["channel_id"]

    invalid_auth_token = user2["token"] 

    valid_uid = user3["auth_user_id"]

    response = rh.channel_invite(invalid_auth_token,channel_id,valid_uid)
    assert response.status_code == 403

def test_positive_casses(clear,user1,user2):
    auth_user_token = user1["token"]

    response = rh.channels_create(auth_user_token,"fakeguy",True)

    response_data = response.json()
    channel_id = response_data["channel_id"]

    new_user_id = user2["auth_user_id"]

    response = requests.post(f"{url}/channel/invite/v2", json={"token": auth_user_token, "channel_id":channel_id , "u_id": new_user_id })

    assert response.status_code == 200

def test_global_owner_gains_owner_permissions():
    rh.clear()
    global_owner = rh.auth_register("fakeguy@gmail.com", "fake123456", "faker", "is_a_faker").json()
    global_owner_tok = global_owner["token"]
    global_owner_id = global_owner["auth_user_id"]
    member1 = rh.auth_register("fakeguy1@gmail.com", "fake123456", "faker1", "is_a_faker1").json()
    member1_id = member1["auth_user_id"]
    member1_token = member1["token"]

    channel1_id = rh.channels_create(member1_token, "channel1", True).json()["channel_id"]

    rh.channel_invite(member1_token, channel1_id, global_owner_id)

    assert rh.channel_addowner(global_owner_tok, channel1_id, global_owner_id).status_code == 200

    assert rh.channel_removeowner(global_owner_tok, channel1_id, member1_id).status_code == 200

def test_invite_removed_user():
    rh.clear()
    global_owner = rh.auth_register("fakeguy@gmail.com", "fake123456", "faker", "is_a_faker").json()
    global_owner_tok = global_owner["token"]
    member1 = rh.auth_register("fakeguy1@gmail.com", "fake123456", "faker1", "is_a_faker1").json()
    member1_id = member1["auth_user_id"]

    channel1_id = rh.channels_create(global_owner_tok, "channel1", True).json()["channel_id"]

    rh.admin_user_remove(global_owner_tok, member1_id)

    assert rh.channel_invite(global_owner_tok, channel1_id, member1_id).status_code == 400
    

