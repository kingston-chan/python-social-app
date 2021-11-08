import json
import requests
import pytest
from src import message, user
from src.config import url
from src.server import channel_invite
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
    dm = response.json()
    return dm
def channel_create_public(token):
    response = requests.post(f"{url}/channels/create/v2", json={"token" : token , "name" : "fake_guys_channel" , "is_public": True })
    channel = response.json()
    return channel
def channel_join(token,channel_id):
    return requests.post(f"{url}/channels/join/v2", json={"token" : token , "channel_id" : channel_id})
#def sending_dm_message():
    #rh.message_send(9999, channel_id, "Hello")
def message_react(token, message_id):
    return requests.post(f"{BASE_URL}/message/react/v1", json={"token" : token, "message_id": message_id, "react_id" : 1})


#==tests==#

def test_unauth_token(clear):
    response = requests.get(f"{url}/notifications/get/v1", params={"token" : 'a'})
    return response.status_code == 403

def test_creating_channel_notif(clear,user1,user2):
    channel = rh.channels_create(user1["token"],"fake_guys_channel", True).json()
    rh.channel_invite(user1["token"],channel["channel_id"],user2["auth_user_id"])
    response = requests.get(f"{url}/notifications/get/v1", params={"token" : user2["token"]})
    assert response.json()["notifications"][0] ==  "{} added you to {}".format(rh.user_profile(user1["token"],user1["auth_user_id"]).json()["user"]["handle_str"],"fake_guys_channel")

def test_creating_dm_notif(clear,user1,user2):
    dm = dm_create(user1["token"],[user2["auth_user_id"]])
    response = requests.get(f"{url}/notifications/get/v1", params={"token" : user2["token"]})
    assert response.json()["notifications"][0] ==  "{} added you to {}".format(rh.user_profile(user1["token"],user1["auth_user_id"]).json()["user"]["handle_str"],rh.dm_details(user1["token"],dm["dm_id"]).json()["name"])

def test_reacted_channel_message(clear,user1,user2):
    channel = rh.channels_create(user1["token"],"fake_guys_channel", True).json()
    message_id = rh.message_send(user1["token"], channel["channel_id"], "Hello")

    rh.channel_invite(user1["token"], channel["channel_id"], user2["auth_user_id"])
    rh.message_react(user2["token"], message_id.json()["message_id"],1)

    response = requests.get(f"{url}/notifications/get/v1", params={"token" : user1["token"]})
    assert response.json()["notifications"][0] ==  "{} reacted to your message in {}".format(rh.user_profile(user2["token"],user2["auth_user_id"]).json()["user"]["handle_str"],"fake_guys_channel")

def test_reacted_dm_message(clear,user1,user2):
    dm = rh.dm_create(user1["token"], [user2["auth_user_id"]]).json()
    message_id = rh.message_senddm(user1['token'], dm["dm_id"], "Hello")
    rh.message_react(user2["token"], message_id.json()["message_id"],1)
    response = requests.get(f"{url}/notifications/get/v1", params={"token" : user1["token"]})
    assert response.json()["notifications"][0] ==  "{} reacted to your message in {}".format(rh.user_profile(user2["token"],user2["auth_user_id"]).json()["user"]["handle_str"],rh.dm_details(user1["token"],dm["dm_id"]).json()["name"])

def test_tagged_message_senddm_notif(clear,user1,user2):
    dm = rh.dm_create(user1["token"], [user2["auth_user_id"]]).json()
    rh.message_senddm(user2["token"], dm["dm_id"], "{} Hello".format('@' + rh.user_profile(user1["token"],user1["auth_user_id"]).json()["user"]["handle_str"]))
    response = requests.get(f"{url}/notifications/get/v1", params={"token" : user1["token"]})
    assert response.json()["notifications"][0] == "{} tagged you in {}: @fakerisafaker Hello".format(rh.user_profile(user2["token"],user2["auth_user_id"]).json()["user"]["handle_str"],rh.dm_details(user1["token"],dm["dm_id"]).json()["name"])

def test_tagged_message_send_notif(clear,user1,user2):
    channel = rh.channels_create(user1["token"],"fake_guys_channel", True).json()
    rh.channel_invite(user1["token"], channel["channel_id"], user2["auth_user_id"])
    rh.message_send(user2["token"], channel["channel_id"], "{} Hello".format('@' + rh.user_profile(user1["token"],user1["auth_user_id"]).json()["user"]["handle_str"]))
    response = requests.get(f"{url}/notifications/get/v1", params={"token" : user1["token"]})
    assert response.json()["notifications"][0] == "{} tagged you in {}: @fakerisafaker Hello".format(rh.user_profile(user2["token"],user2["auth_user_id"]).json()["user"]["handle_str"],"fake_guys_channel")
'''
def test_tagged_message_share():
    return None
'''