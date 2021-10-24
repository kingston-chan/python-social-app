import pytest
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

@pytest.fixture
def clear():
    return rh.clear()

@pytest.fixture
def first_user_data():
    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    return response.json()

@pytest.fixture
def second_user_data():
    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    return response.json()  

def test_details_invalid_channel_id(clear, first_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)

    fake_channel_id = 9999

    response = rh.channel_details(first_user_data["token"], fake_channel_id)

    assert response.status_code == 400

def test_details_uninvited_member(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_details(second_user_data["token"], channel_1)
    assert response.status_code == 403

def test_details_valid_channel_id(clear, first_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    expected_output = {
        "name": "channel_1",
        "is_public": True,
        "owner_members": [
            {
                'u_id': first_user_data["auth_user_id"],
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',                
            }
        ],
        "all_members": [
            {
                'u_id': first_user_data["auth_user_id"],
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',       
            }
        ]
    }

    response = rh.channel_details(first_user_data["token"], channel_1)
    response_data = response.json()
    assert response_data == expected_output

def test_details_unauthorised_user(clear, first_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"] 

    fake_token = "asfapasokfapok"

    response = rh.channel_details(fake_token, channel_1)
    assert response.status_code == 403

def test_details_invited_member(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"] 

    response = rh.channel_invite(first_user_data["token"], channel_1, second_user_data["auth_user_id"])

    expected_output = {
        "name": "channel_1",
        "is_public": True,
        "owner_members": [
            {
                'u_id': first_user_data["auth_user_id"],
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',                
            }
        ],
        "all_members": [
            {
                'u_id': first_user_data["auth_user_id"],
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',       
            },
            {
                'u_id': second_user_data["auth_user_id"],
                'email': 'eagle@gmail.com',
                'name_first': 'team',
                'name_last': 'eagle',
                'handle_str': 'teameagle',  
            }
        ]
    }

    response = rh.channel_details(first_user_data["token"], channel_1)
    response_data = response.json()
    assert response_data == expected_output