import pytest
import requests
import json
from src import config
from src.config import port
import tests.route_helpers as rh

BASE_URL = 'http://127.0.0.1:' + str(port)

#==Fixtures==#
@pytest.fixture
def clear():
    rh.clear()
@pytest.fixture
def user1():
    response = rh.auth_register("fakeguy@gmail.com","fake12345","faker", "is_a_faker")
    return response.json()
@pytest.fixture
def user2():   
    response = rh.auth_register("fakeguy1@gmail.com","fake123451","faker", "is_a_faker1")
    return response.json()

#==tests==#

def test_invalid_channel_id(clear,user1):
    new_user_token = user1["token"]

    response = rh.channels_create(new_user_token,"fakeguy",True)
    response_data = response.json()

    invalid_channel_id = response_data["channel_id"] + 1

    response = rh.channel_join(new_user_token, invalid_channel_id)
    assert response.status_code == 400

def test_invalid_token(clear,user1):
    new_user_token = user1["token"]
    
    response = rh.channels_create(new_user_token,"fakeguy",True)
    
    invalid_token = "0"

    channel_id = response.json()["channel_id"]

    response = rh.channel_join(invalid_token,channel_id)
    
    assert response.status_code == 403    

def test_already_a_member(clear,user1):
    new_user_token = user1["token"]

    response = rh.channels_create(new_user_token, "fakeguy", True)
    channel_id = response.json()["channel_id"]

    response = rh.channel_join(new_user_token,channel_id)

    assert response.status_code == 400   

def test_channel_is_private(clear,user1,user2):
    new_user_token = user1["token"]

    response = rh.channels_create(new_user_token, "fakeguy", False)
    channel_id = response.json()["channel_id"]
    
    new_user_token1 = user2["token"]

    response = rh.channel_join(new_user_token1,channel_id)

    assert response.status_code == 403   

 






