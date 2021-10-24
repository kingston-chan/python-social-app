import requests
import pytest
from src.config import url
from src.auth import auth_logout_v1

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
@pytest.fixture
def user3():
    new_user1 = {"email" : "fakeguy2@gmail.com" , "password": "fake123452","name_first" : "faker", "name_last" : "is_a_faker2" }   
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
def test_invalid_token(clear):
    #requests.delete(f"{url}/clear/v1")
    response = requests.get(f"{url}/dm/list/v1", params={"token" : 1 , "u_ids" : [1]})
    assert response.status_code == 403 


def test_succesful_case1(clear, user1,user2):
    new_user_token = user1["token"]

    user1_token = user2["token"]
    u_id = user2["auth_user_id"]

    dm_create(new_user_token, [u_id])
    list_of_dicts = dm_list(user1_token)

    expected_output = { "dms" : [{'dm_id': 1, 'name': 'fakerisafaker, fakerisafaker1'}]}
    
    assert list_of_dicts == expected_output

def test_succesful_case2(clear, user1,user2,user3):
    owner_token = user1["token"]
    u_id1 = user2["auth_user_id"]
    user1_token = user2["token"]
    u_id2 = user3["auth_user_id"]

    dm_create(owner_token, [u_id1,u_id2])
    list_of_dicts = dm_list(user1_token)

    expected_output = {"dms" : [{"dm_id" : 1 , 'name': "fakerisafaker, fakerisafaker1, fakerisafaker2" }]}

    assert expected_output == list_of_dicts

def test_successfull_case3(clear, user1,user2,user3):
    owner_token = user1["token"]
    u_id1 = user2["auth_user_id"]
    user1_token = user2["token"]
    u_id2 = user3["auth_user_id"]

    dm_create(owner_token, [u_id1,u_id2])
    dm_create(owner_token, [u_id2])

    list_of_dicts = dm_list(user1_token)

    expected_output = {"dms" : [{"dm_id" : 1 , 'name': "fakerisafaker, fakerisafaker1, fakerisafaker2" }]}

    assert expected_output == list_of_dicts

def test_just_owner(clear,user1):
    owner_token = user1["token"]

    dm_create(owner_token, [])

    list_of_dicts = dm_list(owner_token)

    expected_output = {"dms" : [{"dm_id" : 1 , 'name': "fakerisafaker" }]}

    assert expected_output == list_of_dicts


def test_logged_out_creator(clear,user1):
    new_user_token = user1["token"]

    dm_create(new_user_token, [])

    response = requests.post(f"{url}/auth/logout/v1", json={"token" :new_user_token})

    response = requests.get(f"{url}/dm/list/v1", params={"token" : new_user_token })

    assert response.status_code == 403 











