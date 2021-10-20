import json
import requests
import pytest
from requests.sessions import extract_cookies_to_jar
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

#400 is input error
#403 is access error

def test_invlaid_user_ids():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]

    response = requests.post(f"{url}/dm/create/v1", json={"token" : new_user_token , "u_ids" : [0]})
    assert response.status_code == 400   

def test_invlaid_token():
    requests.delete(f"{url}/clear/v1")
    response = requests.post(f"{url}/dm/create/v1", json={"token" : 1 , "u_ids" : [1]})
    assert response.status_code == 403 

def test_one_created_dm():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]

    response = requests.post(f"{url}/dm/create/v1", json={"token" : new_user_token, "u_ids" : []}) 
    dm_id = response.json()

    assert dm_id["dm_id"] == 1

def test_two_created_dm():
    requests.delete(f"{url}/clear/v1")

    user1 = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }
    user2 = {"email" : "fakeguy1@gmail.com" , "password": "fake123456","name_first" : "faker", "name_last" : "is_a_faker1" }

    response = requests.post(f"{url}/auth/register/v2", json=user1) 
    response_data = response.json()
    user1_token = response_data["token"]

    response = requests.post(f"{url}/auth/register/v2", json=user2) 
    response_data = response.json()
    user2_id = response_data["auth_user_id"]

    response = requests.post(f"{url}/dm/create/v1", json={"token" : user1_token, "u_ids" : []}) 
    
    response = requests.post(f"{url}/dm/create/v1", json={"token" : user1_token, "u_ids" : [user2_id]}) 
    dm_id = response.json()

    assert dm_id["dm_id"] == 2

def test_two_identical_dms():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]

    response = requests.post(f"{url}/dm/create/v1", json={"token" : new_user_token, "u_ids" : []}) 
    response = requests.post(f"{url}/dm/create/v1", json={"token" : new_user_token, "u_ids" : []}) 

    dm_id = response.json()

    assert dm_id["dm_id"] == 2

def test_two_dms_with_dm_list():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]

    response = requests.post(f"{url}/dm/create/v1", json={"token" : new_user_token, "u_ids" : []}) 
    response = requests.post(f"{url}/dm/create/v1", json={"token" : new_user_token, "u_ids" : []}) 

    list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : new_user_token })
    expected_output = {"dms" : [{"dm_id" : 1, "name" : "fakerisafaker"},{"dm_id" : 2, "name" : "fakerisafaker"}]}

    assert expected_output == list_of_dicts.json()


def test_users_removed():
    requests.delete(f"{url}/clear/v1")

    user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }
    user1 = {"email" : "fakeguy1@gmail.com" , "password": "fake123456","name_first" : "faker", "name_last" : "is_a_faker1" }

    response = requests.post(f"{url}/auth/register/v2", json=user) 
    response_data = response.json()
    user_token = response_data["token"]


    response = requests.post(f"{url}/auth/register/v2", json=user1) 
    response_data = response.json()
    user1_id = response_data["auth_user_id"]

    response = requests.delete(f"{url}/admin/user/remove/v1", json={"token" : user_token, "u_id" : user1_id})

    response = requests.post(f"{url}/dm/create/v1", json={"token" : user_token, "u_ids" : [user1_id]})

    assert response.status_code == 400  