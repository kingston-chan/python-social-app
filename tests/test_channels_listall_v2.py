import requests
import pytest
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

def test_listall_private_channels():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    user_token = response_data["token"]   

    response = rh.channels_create(user_token, "channel_1", False)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channels_create(user_token, "channel_2", False)
    response_data = response.json()
    channel_2 = response_data["channel_id"]

    response = rh.channels_listall(user_token)
    response_data = response.json()
    
    expected_info = {
        "channels": [{"channel_id": channel_1, "name": "channel_1"}, {"channel_id": channel_2, "name": "channel_2"}],
    }

    assert response_data == expected_info

def test_listall_public_channels():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    user_token = response_data["token"]   

    response = rh.channels_create(user_token, "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channels_create(user_token, "channel_2", True)
    response_data = response.json()
    channel_2 = response_data["channel_id"]

    response = rh.channels_listall(user_token)
    response_data = response.json()
    
    expected_info = {
        "channels": [{"channel_id": channel_1, "name": "channel_1"}, {"channel_id": channel_2, "name": "channel_2"}],
    }
    
    assert response_data == expected_info

def test_listall_private_and_public_channels():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    user_token = response_data["token"]   

    response = rh.channels_create(user_token, "channel_1", False)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channels_create(user_token, "channel_2", True)
    response_data = response.json()
    channel_2 = response_data["channel_id"]

    response = rh.channels_listall(user_token)
    response_data = response.json()
    
    expected_info = {
        "channels": [{"channel_id": channel_1, "name": "channel_1"}, {"channel_id": channel_2, "name": "channel_2"}],
    }
    
    assert response_data == expected_info

def test_unauthorised_token():
    rh.clear()

    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    response_data = response.json()
    user_token = response_data["token"]   

    response = rh.channels_create(user_token, "channel_1", False)
    response_data = response.json()

    fake_token = "asoifjafsa"

    response = rh.channels_listall(fake_token)
    assert response.status_code == 403