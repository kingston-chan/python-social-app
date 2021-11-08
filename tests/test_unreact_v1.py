import pytest, requests
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

#400 is input error
#403 is access error

#==Fixtures==#

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")
@pytest.fixture
def user1():
    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user)
    return response.json()
@pytest.fixture
def user2():
    new_user1 = {"email" : "fakeguy1@gmail.com" , "password": "fake123451","name_first" : "faker", "name_last" : "is_a_faker1" }   
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user1)
    return response.json()

#==tests==#
def test_not_valid_message_id(clear,user1,user2):
    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : user1["token"], "message_id": 0, "react_id" : 1})
    assert response.status_code == 400
def test_not_valid_react_id(clear,user1,user2):
    channel = rh.channels_create(user1["token"], "fake_guy_channel", True).json()
    message_id = rh.message_send(user1["token"],channel["channel_id"], "Hello").json()["message_id"]
    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : user1["token"], "message_id": message_id, "react_id" : 0})
    assert response.status_code == 400 
def test_not_auth_user(clear,user1,user2):
    channel = rh.channels_create(user1["token"], "fake_guy_channel", True).json()
    message_id = rh.message_send(user1["token"],channel["channel_id"], "Hello").json()["message_id"]
    response = requests.post(f"{BASE_URL}/message/react/v1", json={"token" : user2["token"], "message_id": message_id, "react_id" : 1})
    assert response.status_code == 400