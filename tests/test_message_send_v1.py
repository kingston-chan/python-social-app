import pytest
import requests
from src.config import url
import datetime
import json

BASE_URL = url
## =====[ test_message_send_v1.py ]===== ##

# ==== Fixtures ==== #
@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")

@pytest.fixture
def user1():
    user_dict = {
        "email": "user1@email.com",
        "password": "password",
        "name_first": "user",
        "name_last": "name"
    }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_dict)
    print(response.json())
    return response.json()

@pytest.fixture
def user2():
    user_dict = {
        "email": "user2@email.com",
        "password": "password",
        "name_first": "user",
        "name_last": "name"
    }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_dict)
    return response.json()

# ==== Helper functions ==== #
def create_channel(token, name, is_public):
    channel_info = {
        "token": token, 
        "name": name, 
        "is_public": is_public
    }
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response_data = response.json()
    print(f"Channel: {response.json()}")
    return int(response_data['channel_id'])

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_invalid_channel(clear, user1):
    pass

def test_message_too_long(clear, user1):
    pass

def test_message_too_short(clear, user1):
    pass

## Access Error - 403 ##
def test_real_unauthorised_user(clear, user1, user2):
    pass

def test_dummy_unauthorised_user(clear, user1):
    pass

# ==== Tests - Valids ==== #
def test_one_user_sends_one_message_in_one_channel(clear, user1):
    pass

def test_one_user_sends_one_message_in_multiple_channels(clear, user1):
    pass

def test_one_user_sends_multiple_messages_in_one_channel(clear, user1):
    pass

def test_one_user_sends_multiple_messages_in_multiple_channels(clear, user1):
    pass

def test_multiple_users_sends_one_message_in_one_channel(clear, user1, user2):
    pass

def test_multiple_users_sends_one_message_in_multiple_channels(clear, user1, user2):
    pass

def test_multiple_users_sends_multiple_messages_in_one_channel(clear, user1, user2):
    pass

def test_multiple_users_sends_multiple_messages_in_multiple_channels(clear, user1, user2):
    pass

# ==== Future Tests for Future Functions ==== #

def test_one_user_sends_one_message_in_private_channel(clear, user1):
    pass

def test_one_user_sends_one_message_in_private_and_public_channel(clear, user1):
    pass

