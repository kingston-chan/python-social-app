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
def test_removing_one_dm(clear,user1):
    new_user_token = user1["token"]

    dm_id = rh.dm_create(new_user_token, [])

    rh.dm_remove(new_user_token,dm_id.json()["dm_id"]) 

    output = rh.dm_list(new_user_token)

    expected_output = []


    assert expected_output == output.json()["dms"]

def test_invalid_dm_id(clear,user1):
    new_user_token = user1["token"]

    response = rh.dm_remove(new_user_token,1) 
    assert response.status_code == 400 

def test_invlaid_token(clear):
    response = rh.dm_remove(1,1) 
    assert response.status_code == 403 


def test_not_auth_user(clear,user1,user2):
    user1_token = user1["token"]

    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]

    dm_id = rh.dm_create(user1_token, [user2_id]).json()
    
    response = rh.dm_remove(user2_token, dm_id["dm_id"])
    assert response.status_code == 403 

def test_removing_one_dm_with_two_created(clear,user1,user2):
    user1_token = user1["token"]

    user2_id = user2["auth_user_id"]

    rh.dm_create(user1_token, [])
    response = rh.dm_create(user1_token, [user2_id])
    dm_id = response.json()["dm_id"]

    rh.dm_remove(user1_token,dm_id)
    response = rh.dm_list(user1_token)
    output = response.json()

    expected_outcome = {"dms" : [{"dm_id" : 1 , "name" : "fakerisafaker"}]}

    assert expected_outcome == output