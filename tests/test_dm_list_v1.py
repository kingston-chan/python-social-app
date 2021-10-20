import requests
import pytest
from src.config import url
from src.auth import auth_logout_v1

BASE_URL = url

#400 is input error
#403 is access error

def test_invalid_token():
    requests.delete(f"{url}/clear/v1")
    response = requests.get(f"{url}/dm/list/v1", params={"token" : 1 , "u_ids" : [1]})
    assert response.status_code == 403 


def test_succesful_case1():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]

    new_user = {"email" : "fakeguy1@gmail.com" , "password": "fake123456","name_first" : "faker", "name_last" : "is_a_faker1" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    user1_token = response_data["token"]
    u_id = response_data["auth_user_id"]

    response = requests.post(f"{BASE_URL}/dm/create/v1", json={ "token" : new_user_token, "u_ids" : [u_id] })
    response_data = response.json()

    list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : user1_token })

    list_of_dicts = list_of_dicts.json()

    expected_output = { "dms" : [{'dm_id': 1, 'name': 'fakerisafaker, fakerisafaker1'}]}
    
    assert list_of_dicts == expected_output

def test_succesful_case2():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }
    new_user1 = {"email" : "fakeguy1@gmail.com" , "password": "fake123456","name_first" : "faker", "name_last" : "is_a_faker1" }
    new_user2 = {"email" : "fakeguy2@gmail.com" , "password": "fake123457","name_first" : "faker", "name_last" : "is_a_faker2" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user)
    owner_token = response.json()["token"]
    response = requests.post(f"{url}/auth/register/v2", json=new_user1)
    u_id1 = response.json()["auth_user_id"]
    user1_token = response.json()["token"]
    response = requests.post(f"{url}/auth/register/v2", json=new_user2)
    u_id2 = response.json()["auth_user_id"]

    response = requests.post(f"{BASE_URL}/dm/create/v1", json={ "token" : owner_token, "u_ids" : [u_id1,u_id2] })
        
    list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : user1_token })

    output = list_of_dicts.json()

    expected_output = {"dms" : [{"dm_id" : 1 , 'name': "fakerisafaker, fakerisafaker1, fakerisafaker2" }]}

    assert expected_output == output


def test_successfull_case3():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }
    new_user1 = {"email" : "fakeguy1@gmail.com" , "password": "fake123456","name_first" : "faker", "name_last" : "is_a_faker1" }
    new_user2 = {"email" : "fakeguy2@gmail.com" , "password": "fake123457","name_first" : "faker", "name_last" : "is_a_faker2" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user)
    owner_token = response.json()["token"]
    response = requests.post(f"{url}/auth/register/v2", json=new_user1)
    u_id1 = response.json()["auth_user_id"]
    user1_token = response.json()["token"]
    response = requests.post(f"{url}/auth/register/v2", json=new_user2)
    u_id2 = response.json()["auth_user_id"]  

    response = requests.post(f"{BASE_URL}/dm/create/v1", json={ "token" : owner_token, "u_ids" : [u_id1,u_id2] })
    response = requests.post(f"{BASE_URL}/dm/create/v1", json={ "token" : owner_token, "u_ids" : [u_id2] })
    
    list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : user1_token })

    output = list_of_dicts.json()

    expected_output = {"dms" : [{"dm_id" : 1 , 'name': "fakerisafaker, fakerisafaker1, fakerisafaker2" }]}

    assert expected_output == output

def test_just_owner():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user)
    owner_token = response.json()["token"] 

    response = requests.post(f"{BASE_URL}/dm/create/v1", json={ "token" : owner_token, "u_ids" : [] })
    
    list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : owner_token })

    output = list_of_dicts.json()

    expected_output = {"dms" : [{"dm_id" : 1 , 'name': "fakerisafaker" }]}

    assert expected_output == output


def test_logged_out_creator():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user)

    response_data = response.json()
    new_user_token = {"token" : response_data["token"]}

    response = requests.post(f"{BASE_URL}/dm/create/v1", json={ "token" : new_user_token, "u_ids" : [] })
    
    response = requests.post(f"{url}/auth/logout/v1", json=new_user_token)

    response = requests.get(f"{url}/dm/list/v1", params={"token" : new_user_token })

    assert response.status_code == 403 











