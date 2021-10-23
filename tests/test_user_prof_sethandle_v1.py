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
def test_input_string_too_long(clear,user1):
    user_token = user1["token"]
    
    new_handle = "thispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfake"

    response = rh.user_profile_sethandle(user_token,new_handle)   

    assert response.status_code == 400

def test_non_alphanumeric_inputs(clear,user1):
    user_token = user1["token"]
    
    new_handle = "***********"

    response = rh.user_profile_sethandle(user_token,new_handle) 

    assert response.status_code == 400

def test_handle_string_is_used(clear, user1,user2):
    user_token = user1["token"]

    new_handle = "thispersonisfake"

    rh.user_profile_sethandle(user_token,new_handle) 

    user_token = user2["token"]


    response = rh.user_profile_sethandle(user_token,new_handle)
    assert response.status_code == 400

def test_invalid_token(clear):
    new_handle = "thispersonisfake"
    response = rh.user_profile_sethandle(1,new_handle)    
    assert response.status_code == 403

def test_succesful_case(clear,user1):
    user_token = user1["token"]
    
    new_handle = "thispersonisfake"

    response = rh.user_profile_sethandle(user_token,new_handle)
    assert response.status_code == 200

def test_handle_already_used2(clear,user1,user2):
    user_token = user2["token"]
    
    new_handle = "thispersonisafake"

    response = rh.user_profile_sethandle(user_token,new_handle) 

    assert response.status_code == 200
