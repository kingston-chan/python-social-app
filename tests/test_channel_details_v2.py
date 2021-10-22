import pytest
import requests
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

def test_details_invalid_channel_id():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    user_token = response_data["token"]

    response = rh.channels_create(user_token, "channel_1", True)

    fake_channel_id = 9999

    response = rh.channel_details(user_token, fake_channel_id)

    assert response.status_code == 400

def test_details_uninvited_member():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_user_token = response_data["token"]    

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    uninvited_user_token = response_data["token"]    

    response = rh.channels_create(owner_user_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_details(uninvited_user_token, channel_1)
    assert response.status_code == 403

def test_details_valid_channel_id():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    user_token = response_data["token"]
    user_id = response_data["auth_user_id"]

    response = rh.channels_create(user_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    expected_output = {
        "name": "channel_1",
        "is_public": True,
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

    response = rh.channel_details(user_token, channel_1)
    response_data = response.json()
    assert response_data == expected_output

def test_details_unauthorised_user():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    user_token = response_data["token"]

    response = rh.channels_create(user_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"] 

    fake_user_token = "asfapasokfapok"

    response = rh.channel_details(fake_user_token, channel_1)
    assert response.status_code == 403

def test_details_invited_member():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_user_token = response_data["token"] 
    owner_user_id = response_data["auth_user_id"] 

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_user_token = response_data["token"]
    invited_user_id = response_data["auth_user_id"]

    response = rh.channels_create(owner_user_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"] 

    response = rh.channel_invite(owner_user_token, channel_1, invited_user_id)

    expected_output = {
        "name": "channel_1",
        "is_public": True,
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

    response = rh.channel_details(invited_user_token, channel_1)
    response_data = response.json()
    assert response_data == expected_output