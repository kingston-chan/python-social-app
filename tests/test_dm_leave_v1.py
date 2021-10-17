import pytest
import requests
from src.config import url

BASE_URL = url

def test_dm_leave_invalid_dm_id():
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

    dm_info = {
        "token": owner_token,
        "u_ids": [invited_member_u_id]
    }

    response = requests.post(f"{BASE_URL}/dm/create/v1", json=dm_info)
    response_data = response.json()

    fake_dm_id = 9999

    dm_leave_info = {
        "token": invited_member_token,
        "dm_id": fake_dm_id
    }

    response = requests.post(f"{BASE_URL}/dm/leave/v1", json=dm_leave_info)

    assert response.status_code == 400

def test_dm_leave_not_a_member_of_dm():
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
    invited_member_u_id = response_data["auth_user_id"]

    uninvited_member_data = {
        "email": "butcher@gmail.com",
        "password": "password",
        "name_first": "knife",
        "name_last": "butcher"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=uninvited_member_data)
    response_data = response.json()
    uninvited_member_token = response_data["token"]

    dm_info = {
        "token": owner_token,
        "u_ids": [invited_member_u_id]
    }

    response = requests.post(f"{BASE_URL}/dm/create/v1", json=dm_info)
    response_data = response.json()
    dm_id = response_data["dm_id"]

    dm_leave_info = {
        "token": uninvited_member_token,
        "dm_id": dm_id
    }

    response = requests.post(f"{BASE_URL}/dm/leave/v1", json=-dm_leave_info)

    assert response.status_code == 403

def test_dm_leave_unauthorised_token():
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
    invited_member_u_id = response_data["auth_user_id"]

    dm_info = {
        "token": owner_token,
        "u_ids": [invited_member_u_id]
    }

    response = requests.post(f"{BASE_URL}/dm/create/v1", json=dm_info)
    response_data = response.json()
    dm_id = response_data["dm_id"]
    
    fake_token = "asfoipjasoifj"

    dm_leave_info = {
        "token": fake_token,
        "dm_id": dm_id
    }

    response = requests.post(f"{BASE_URL}/dm/leave/v1", json=dm_leave_info)

    assert response.status_code == 403

def test_dm_leave_valid():
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

    dm_info = {
        "token": owner_token,
        "u_ids": [invited_member_u_id]
    }

    response = requests.post(f"{BASE_URL}/dm/create/v1", json=dm_info)
    response_data = response.json()
    dm_id = response_data["dm_id"]

    dm_leave_info = {
        "token": invited_member_token,
        "dm_id": dm_id
    }

    response = requests.post(f"{BASE_URL}/dm/leave/v1", json=-dm_leave_info) 

    dm_details_info = {
        "token": owner_token,
        "dm_id": dm_id
    }

    response = requests.get(f"{BASE_URL}/dm/details/v1", params=dm_details_info)
    response_data = response.json()

    expected_output = {
        "name": "keefevuong, teameagle",
        "members": [
            {
                'u_id': owner_u_id,
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',     
            }
        ]
    }

    assert response_data == expected_output

def test_dm_leave_owner_leaves_dm():
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

    dm_info = {
        "token": owner_token,
        "u_ids": [invited_member_u_id]
    }

    response = requests.post(f"{BASE_URL}/dm/create/v1", json=dm_info)
    response_data = response.json()
    dm_id = response_data["dm_id"]

    dm_leave_info = {
        "token": owner_token,
        "dm_id": dm_id
    }

    response = requests.post(f"{BASE_URL}/dm/leave/v1", json=-dm_leave_info) 

    dm_details_info = {
        "token": invited_member_token,
        "dm_id": dm_id
    }

    response = requests.get(f"{BASE_URL}/dm/details/v1", params=dm_details_info)
    response_data = response.json()

    expected_output = {
        "name": "keefevuong, teameagle",
        "members": [
            {
                'u_id': invited_member_u_id,
                'email': 'eagle@gmail.com',
                'name_first': 'team',
                'name_last': 'eagle',
                'handle_str': 'teameagle',     
            }
        ]
    }

    assert response_data == expected_output