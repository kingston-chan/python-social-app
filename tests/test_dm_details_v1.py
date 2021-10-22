import pytest
import requests
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

def test_dm_details_multiple_users():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_token = response_data["token"]  
    invited_member_u_id = response_data["auth_user_id"]

    response = rh.auth_register("butcher@gmail.com", "password", "knife", "butcher")

    response = rh.dm_create(owner_token, [invited_member_u_id])
    response_data = response.json()
    dm_id = response_data["dm_id"]

    response = rh.dm_details(invited_member_token, dm_id)
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
            },
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


def test_dm_details_invalid_dm_id():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_u_id = response_data["auth_user_id"]

    response = rh.dm_create(owner_token, [invited_member_u_id])
    response_data = response.json()

    fake_dm_id = 99999

    response = rh.dm_details(owner_token, fake_dm_id)

    assert response.status_code == 400

def test_dm_details_not_a_member():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_u_id = response_data["auth_user_id"]

    response = rh.auth_register("butcher@gmail.com", "password", "knife", "butcher")
    response_data = response.json()
    uninvited_member_token = response_data["token"]  

    response = rh.dm_create(owner_token, [invited_member_u_id])
    response_data = response.json()
    dm_id = response_data["dm_id"]

    response = rh.dm_details(uninvited_member_token, dm_id)

    assert response.status_code == 403

def test_dm_details_valid():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  
    owner_u_id = response_data["auth_user_id"]

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_u_id = response_data["auth_user_id"]

    response = rh.dm_create(owner_token, [invited_member_u_id])
    response_data = response.json()
    dm_id = response_data["dm_id"]

    response = rh.dm_details(owner_token, dm_id)
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
            },
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

def test_dm_details_unauthorised_token():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    owner_token = response_data["token"]  

    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    response_data = response.json()
    invited_member_u_id = response_data["auth_user_id"]

    response = rh.dm_create(owner_token, [invited_member_u_id])
    response_data = response.json()
    dm_id = response_data["dm_id"]

    fake_token = "asfijasoifjas"

    response = rh.dm_details(fake_token, dm_id)

    assert response.status_code == 403

    