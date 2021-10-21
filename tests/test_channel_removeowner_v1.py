import pytest
import requests
from src.config import url

BASE_URL = url

def test_removeowner_globalowner():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"        
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_data)
    response_data = response.json()
    owner_token = response_data["token"]
    owner_u_id = response_data["auth_user_id"]

    invited_member_data = {
        "email": "eagle@gmail.com",
        "password": "password",
        "name_first": "team",
        "name_last": "eagle"   
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=invited_member_data)
    response_data = response.json()
    invited_member_token = response_data["token"]
    invited_member_u_id = response_data["auth_user_id"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    join_info = {
        "token": invited_member_token,
        "channel_id": channel_1
    }

    response = requests.post(f"{BASE_URL}/channel/join/v2", json=join_info)

    add_owner_info = {
        "token": owner_token,
        "channel_id": channel_1,
        "u_id": invited_member_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json=add_owner_info)

    remove_owner_info = {
        "token": owner_token,
        "channel_id": channel_1,
        "u_id": owner_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json=remove_owner_info)

    add_owner_info["u_id"] = owner_u_id

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json=add_owner_info)

    assert response.status_code == 200
    

def test_removeowner_valid():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"        
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_data)
    response_data = response.json()
    owner_token = response_data["token"]
    owner_u_id = response_data["auth_user_id"]

    invited_member_data = {
        "email": "eagle@gmail.com",
        "password": "password",
        "name_first": "team",
        "name_last": "eagle"   
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=invited_member_data)
    response_data = response.json()
    invited_member_token = response_data["token"]
    invited_member_u_id = response_data["auth_user_id"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    join_info = {
        "token": invited_member_token,
        "channel_id": channel_1
    }

    response = requests.post(f"{BASE_URL}/channel/join/v2", json=join_info)

    add_owner_info = {
        "token": owner_token,
        "channel_id": channel_1,
        "u_id": invited_member_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json=add_owner_info)

    remove_owner_info = {
        "token": owner_token,
        "channel_id": channel_1,
        "u_id": invited_member_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json=remove_owner_info)
    
    channel_info = {
        "token": invited_member_token,
        "channel_id": channel_1
    }

    response = requests.get(f"{BASE_URL}/channel/details/v2", params=channel_info)
    response_data = response.json()

    assert response_data["owner_members"][0]["u_id"] == owner_u_id

def test_removeowner_invalid_channel_id():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"        
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_data)
    response_data = response.json()
    owner_token = response_data["token"]
    owner_u_id = response_data["auth_user_id"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()

    fake_channel_id = 9999

    remove_owner_info = {
        "token": owner_token,
        "channel_id": fake_channel_id,
        "u_id": owner_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json=remove_owner_info)
    
    assert response.status_code == 400

def tests_removeowner_no_more_owners():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"        
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_data)
    response_data = response.json()
    owner_token = response_data["token"]
    owner_u_id = response_data["auth_user_id"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    remove_owner_info = {
        "token": owner_token,
        "channel_id": channel_1,
        "u_id": owner_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json=remove_owner_info)
    
    assert response.status_code == 400

def test_removeowner_invalid_user_id():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"        
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_data)
    response_data = response.json()
    owner_token = response_data["token"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    fake_user_id = 9999

    remove_owner_info = {
        "token": owner_token,
        "channel_id": channel_1,
        "u_id": fake_user_id
    }

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json=remove_owner_info)
    
    assert response.status_code == 400

def tests_removeowner_unauthorised_owner():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"        
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_data)
    response_data = response.json()
    owner_token = response_data["token"]
    owner_u_id = response_data["auth_user_id"]

    second_owner_data = {
        "email": "butchere@gmail.com",
        "password": "password",
        "name_first": "knife",
        "name_last": "butcher"     
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=second_owner_data)
    response_data = response.json()
    second_owner_token = response_data["token"]
    second_owner_u_id = response_data["auth_user_id"]

    invited_member_data = {
        "email": "eagle@gmail.com",
        "password": "password",
        "name_first": "team",
        "name_last": "eagle"   
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=invited_member_data)
    response_data = response.json()
    invited_member_token = response_data["token"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    join_info = {
        "token": second_owner_token,
        "channel_id": channel_1
    }

    response = requests.post(f"{BASE_URL}/channel/join/v2", json=join_info)

    join_info["token"] = invited_member_token

    response = requests.post(f"{BASE_URL}/channel/join/v2", json=join_info)

    add_owner_info = {
        "token": owner_token,
        "channel_id": channel_1,
        "u_id": second_owner_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json=add_owner_info)

    remove_owner_info = {
        "token": invited_member_token,
        "channel_id": channel_1,
        "u_id": owner_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json=remove_owner_info)
    
    assert response.status_code == 403

def tests_removeowner_thats_not_an_owner():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"        
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_data)
    response_data = response.json()
    owner_token = response_data["token"]

    invited_member_data = {
        "email": "eagle@gmail.com",
        "password": "password",
        "name_first": "team",
        "name_last": "eagle"   
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=invited_member_data)
    response_data = response.json()
    invited_member_token = response_data["token"]
    invited_member_u_id = response_data["auth_user_id"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    join_info = {
        "token": invited_member_token,
        "channel_id": channel_1
    }

    response = requests.post(f"{BASE_URL}/channel/join/v2", json=join_info)

    remove_owner_info = {
        "token": owner_token,
        "channel_id": channel_1,
        "u_id": invited_member_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json=remove_owner_info)
    
    assert response.status_code == 400

def test_removeowner_unauthorised_token():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"        
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_data)
    response_data = response.json()
    owner_token = response_data["token"]
    owner_u_id = response_data["auth_user_id"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    fake_token = "aosfjaoifsjiasfoa"

    remove_owner_info = {
        "token": fake_token,
        "channel_id": channel_1,
        "u_id": owner_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json=remove_owner_info)
    
    assert response.status_code == 403

def test_removeowner_global_owner():
    requests.delete(f"{BASE_URL}/clear/v1")

    invited_member_data = {
        "email": "eagle@gmail.com",
        "password": "password",
        "name_first": "team",
        "name_last": "eagle"   
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=invited_member_data)
    response_data = response.json()
    invited_member_token = response_data["token"]

    owner_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"        
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_data)
    response_data = response.json()
    owner_token = response_data["token"]
    owner_u_id = response_data["auth_user_id"]

    channel_1_info = {
        "token": owner_token,
        "name": "channel_1",
        "is_public": True
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    join_info = {
        "token": invited_member_token,
        "channel_id": channel_1
    }

    response = requests.post(f"{BASE_URL}/channel/join/v2", json=join_info)

    remove_owner_info = {
        "token": invited_member_token,
        "channel_id": channel_1,
        "u_id": owner_u_id
    }

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json=remove_owner_info)

    assert response.status_code == 400
