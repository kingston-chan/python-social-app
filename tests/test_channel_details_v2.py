import pytest
import requests
from src.config import url

BASE_URL = url

def test_details_invalid_channel_id():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()
    user_token = response_data["token"]

    channel_info = {
        "token": user_token,
        "name": "channel_1",
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)

    fake_channel_id = 9999

    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": user_token, "channel_id": fake_channel_id})

    assert response.status_code == 400

def test_details_uninvited_member():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_user_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"
    }

    uninvited_user_data = {
        "email": "eagle@gmail.com",
        "password": "password",
        "name_first": "team",
        "name_last": "eagle"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_user_data)
    response_data = response.json()
    owner_user_token = response_data["token"]    

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=uninvited_user_data)
    response_data = response.json()
    uninvited_user_token = response_data["token"]    

    channel_info = {
        "token": owner_user_token,
        "name": "channel_1",
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": uninvited_user_token, "channel_id": channel_1})
    assert response.status_code == 403

def test_details_valid_channel_id():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()
    user_token = response_data["token"]
    user_id = response_data["auth_user_id"]

    channel_info = {
        "token": user_token,
        "name": "channel_1",
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    expected_output = {
        "name": "channel_1",
        "is_public": "True",
        "owner_members": [
            {
                'u_id': user_id,
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',                
            }
        ],
        "all_members": [
            {
                'u_id': user_id,
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',       
            }
        ]
    }

    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": user_token, "channel_id": channel_1})
    response_data = response.json()
    assert response_data == expected_output

def test_details_unauthorised_user():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()
    user_token = response_data["token"]

    channel_info = {
        "token": user_token,
        "name": "channel_1",
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"] 

    fake_user_token = "asfapasokfapok"

    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": fake_user_token, "channel_id": channel_1})
    assert response.status_code == 403

def test_details_invited_member():
    requests.delete(f"{BASE_URL}/clear/v1")

    owner_user_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"
    }

    invited_user_data = {
        "email": "eagle@gmail.com",
        "password": "password",
        "name_first": "team",
        "name_last": "eagle"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=owner_user_data)
    response_data = response.json()
    owner_user_token = response_data["token"] 
    owner_user_id = response_data["auth_user_id"] 

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=invited_user_data)
    response_data = response.json()
    invited_user_token = response_data["token"]
    invited_user_id = response_data["auth_user_id"]

    channel_info = {
        "token": owner_user_token,
        "name": "channel_1",
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"] 

    channel_invite_info = {
        "token": owner_user_token,
        "channel_id": channel_1,
        "u_id": invited_user_id
    }

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json=channel_invite_info)

    expected_output = {
        "name": "channel_1",
        "is_public": "True",
        "owner_members": [
            {
                'u_id': owner_user_id,
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',                
            }
        ],
        "all_members": [
            {
                'u_id': owner_user_id,
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',       
            },
            {
                'u_id': invited_user_id,
                'email': 'eagle@gmail.com',
                'name_first': 'team',
                'name_last': 'eagle',
                'handle_str': 'teameagle',  
            }
        ]
    }

    response = requests.get(f"{BASE_URL}/channel/details/v2", params={"token": invited_user_token, "channel_id": channel_1})
    response_data = response.json()
    assert response_data == expected_output