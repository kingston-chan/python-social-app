import json
import requests
import pytest
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
#==Helper Functions==#
def dm_list(token):
    list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : token })
    return list_of_dicts.json()
def dm_create(token, u_ids):
    response = requests.post(f"{url}/dm/create/v1", json={"token" : token , "u_ids" : u_ids})
    dm_id = response.json()
    return dm_id

#==tests==#

def test_invlaid_user_ids(clear, user1):
    new_user_token = user1["token"]
    response = requests.post(f"{url}/dm/create/v1", json={"token" : new_user_token , "u_ids" : [0]})
    assert response.status_code == 400   

def test_invlaid_token(clear):
    response = requests.post(f"{url}/dm/create/v1", json={"token" : 1 , "u_ids" : [1]})
    assert response.status_code == 403 

def test_one_created_dm(clear, user1):
    new_user_token = user1["token"]

    dm_id = dm_create(new_user_token,[])

    assert dm_id["dm_id"] == 1

def test_two_created_dm(clear, user1,user2):
    user1_token = user1["token"]
    user2_id = user2["auth_user_id"]


    dm_create(user1_token,[])
    dm_id = dm_create(user1_token,[user2_id])

    assert dm_id["dm_id"] == 2

def test_two_identical_dms(clear, user1):

    new_user_token = user1["token"]

    dm_create(new_user_token,[])
    
    dm_id = dm_create(new_user_token,[])

    assert dm_id["dm_id"] == 2

def test_two_dms_with_dm_list(clear,user1):
    new_user_token = user1["token"]

    dm_create(new_user_token,[])
    dm_create(new_user_token,[])

    list_of_dicts = dm_list(new_user_token)
    expected_output = {"dms" : [{"dm_id" : 1, "name" : "fakerisafaker"},{"dm_id" : 2, "name" : "fakerisafaker"}]}

    assert expected_output == list_of_dicts


def test_users_removed(clear, user1,user2):
   
    user_token = user1["token"]
    user1_id = user2["auth_user_id"]

    response = requests.delete(f"{url}/admin/user/remove/v1", json={"token" : user_token, "u_id" : user1_id})
    response = requests.post(f"{url}/dm/create/v1", json={"token" : user_token, "u_ids" : [user1_id]})

    assert response.status_code == 400  