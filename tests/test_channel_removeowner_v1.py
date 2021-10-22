import pytest
import requests
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

def test_removeowner_globalowner():
    rh.clear()

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

    response = rh.channel_removeowner(owner_token, channel_1, owner_u_id)

    response = rh.channel_addowner(owner_token, channel_1, owner_u_id)

    assert response.status_code == 200
    

def test_removeowner_valid():
    rh.clear()

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

    response = rh.channel_removeowner(owner_token, channel_1, invited_member_u_id)

    response = rh.channel_details(invited_member_token, channel_1)
    response_data = response.json()

    assert response_data["owner_members"][0]["u_id"] == owner_u_id

def test_removeowner_invalid_channel_id():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()

    fake_channel_id = 9999

    response = rh.channel_removeowner(owner_token, fake_channel_id, owner_u_id)
    
    assert response.status_code == 400

def tests_removeowner_no_more_owners():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_removeowner(owner_token, channel_1, owner_u_id)
    
    assert response.status_code == 400

def test_removeowner_invalid_user_id():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    fake_user_id = 9999

    response = rh.channel_removeowner(owner_token, channel_1, fake_user_id)
    
    assert response.status_code == 400

def tests_removeowner_unauthorised_owner():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    response = rh.auth_register("butcher@gmail.com", "password", "knife", "butcher")
    response_data = response.json()
    second_owner_token = response_data["token"]  
    second_owner_u_id = response_data["auth_user_id"]

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_token = response_data["token"]   

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(second_owner_token, channel_1)

    response = rh.channel_join(invited_member_token, channel_1)

    response = rh.channel_addowner(owner_token, channel_1, second_owner_u_id)

    response = rh.channel_removeowner(invited_member_token, channel_1, owner_u_id)
    
    assert response.status_code == 403

def tests_removeowner_thats_not_an_owner():
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

    response = rh.channel_removeowner(owner_token, channel_1, invited_member_u_id)
    
    assert response.status_code == 400

def test_removeowner_unauthorised_token():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    fake_token = "aosfjaoifsjiasfoa"

    response = rh.channel_removeowner(fake_token, channel_1, owner_u_id)
    
    assert response.status_code == 403

def test_removeowner_global_owner():
    rh.clear()

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_token = response_data["token"]   

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    response = rh.channels_create(owner_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(invited_member_token, channel_1)

    response = rh.channel_removeowner(invited_member_token, channel_1, owner_u_id)

    assert response.status_code == 400
