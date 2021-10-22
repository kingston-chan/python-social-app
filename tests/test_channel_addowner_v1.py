import pytest
import requests
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

def test_addowner_valid():
    rh.clear()

    owner_list = []

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_token = response_data["token"]    
    invited_member_u_id = response_data["auth_user_id"]

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(invited_member_token, channel_1)

    response = rh.channel_addowner(owner_token, channel_1, invited_member_u_id)

    response = rh.channel_details(invited_member_token, channel_1)
    response_data = response.json()

    owner_list.append(response_data["owner_members"][0]["u_id"])
    owner_list.append(response_data["owner_members"][1]["u_id"])

    expected_outcome = [owner_u_id, invited_member_u_id]

    assert owner_list == expected_outcome

def test_addowner_invalid_channel_id():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_token = response_data["token"]    
    invited_member_u_id = response_data["auth_user_id"]

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(invited_member_token, channel_1)

    fake_channel_id = 9999

    response = rh.channel_addowner(owner_token, fake_channel_id, invited_member_u_id)
    
    assert response.status_code == 400
def test_addowner_invalid_user_id():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_token = response_data["token"]    

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(invited_member_token, channel_1)

    fake_user_id = 9999

    response = rh.channel_addowner(owner_token, channel_1, fake_user_id)

    assert response.status_code == 400

def test_addowner_uninvited_member():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    uninvited_member_u_id= response_data["auth_user_id"]  

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_addowner(owner_token, channel_1, uninvited_member_u_id)

    assert response.status_code == 400

def test_addowner_already_owner():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_addowner(owner_token, channel_1, owner_u_id)
    
    assert response.status_code == 400

def test_addowner_no_owner_perms():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_token= response_data["token"]  

    response = rh.auth_register("butcher@gmail.com", "password", "knife", "butcher")
    response_data = response.json()
    invited_member_token_2= response_data["token"]  
    invited_member_u_id_2 = response_data["auth_user_id"]

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(invited_member_token, channel_1)

    response = rh.channel_join(invited_member_token_2, channel_1)

    response = rh.channel_addowner(invited_member_token, channel_1, invited_member_u_id_2)

    assert response.status_code == 403

def test_addowner_global_owner():
    rh.clear()

    owner_list = []

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_token= response_data["token"]  
    invited_member_u_id = response_data["auth_user_id"]

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(invited_member_token, channel_1)

    response = rh.channel_addowner(invited_member_token, channel_1, invited_member_u_id)

    response = rh.channel_details(invited_member_token, channel_1)
    response_data = response.json()

    owner_list.append(response_data["owner_members"][0]["u_id"])
    owner_list.append(response_data["owner_members"][1]["u_id"])

    expected_outcome = [invited_member_u_id, owner_u_id]

    assert owner_list == expected_outcome


def test_addowner_unauthorised_token():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_token = response_data["token"]  
    invited_member_u_id = response_data["auth_user_id"]

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(invited_member_token, channel_1)

    fake_token = "aoisjfaoisjfja"

    response = rh.channel_addowner(fake_token, channel_1, invited_member_u_id)
    
    assert response.status_code == 403