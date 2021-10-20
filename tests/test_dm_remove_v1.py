import json
import requests
import pytest
from src.config import url

BASE_URL = url

#400 is input error
#403 is access error

def test_removing_one_dm():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]

    response = requests.post(f"{url}/dm/create/v1", json={"token" : new_user_token, "u_ids" : []}) 
    dm_id = response.json()["dm_id"]

    response = requests.delete(f"{url}/dm/remove/v1", json={"token" : new_user_token , "dm_id" : dm_id})
    output = response.json()

    output = requests.get(f"{url}/dm/list/v1", params={"token" : new_user_token })


    expected_output = []


    assert expected_output == output.json()["dms"]

def test_invalid_dm_id():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]

    response = requests.delete(f"{url}/dm/remove/v1", json={"token" : new_user_token , "dm_id" : 1})

    assert response.status_code == 400 

def test_invlaid_token():
    requests.delete(f"{url}/clear/v1")
    response = requests.delete(f"{url}/dm/remove/v1", json={"token" : 1 , "dm_id" : 1})
    assert response.status_code == 403 


def test_not_auth_user():
    requests.delete(f"{url}/clear/v1")

    user1 = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }
    user2 = {"email" : "fakeguy1@gmail.com" , "password": "fake123456","name_first" : "faker", "name_last" : "is_a_faker1" }

    response = requests.post(f"{url}/auth/register/v2", json=user1) 
    response_data = response.json()
    user1_token = response_data["token"]

    response = requests.post(f"{url}/auth/register/v2", json=user2) 
    response_data = response.json()
    user2_token = response_data["token"]
    user2_id = response_data["auth_user_id"]

    response = requests.post(f"{url}/dm/create/v1", json={"token" : user1_token, "u_ids" : [user2_id]}) 
    dm_id = response.json()["dm_id"]
    response = requests.delete(f"{url}/dm/remove/v1", json={"token" : user2_token, "dm_id" : dm_id})
    assert response.status_code == 403 

def test_removing_one_dm_with_two_created():
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
    dm_id = response.json()["dm_id"]

    response = requests.delete(f"{url}/dm/remove/v1", json={"token" : user1_token, "dm_id" : dm_id})

    response = requests.get(f"{url}/dm/list/v1", params={"token" : user1_token})
    output = response.json()

    expected_outcome = {"dms" : [{"dm_id" : 1 , "name" : "fakerisafaker"}]}

    assert expected_outcome == output