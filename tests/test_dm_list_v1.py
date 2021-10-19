import requests
import pytest
from src.config import url

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
    owner_uid = response_data["auth_user_id"]

    new_user = {"email" : "fakeguy1@gmail.com" , "password": "fake123456","name_first" : "faker1", "name_last" : "is_a_faker1" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    input_token = response_data["token"]
    u_id = response_data["auth_user_id"]

    response = requests.post(f"{BASE_URL}/dm/create/v1", json={ "token" : new_user_token, "u_ids" : [u_id] })
    response_data = response.json()
    dm_id = response_data["dm_id"]

    list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : input_token })

    list_of_dicts = list_of_dicts.json()

    expected_output = { "dms" : [{'dm_id': 1, 'name': 'faker1isafaker, fakerisafaker1'}]}
    
    assert list_of_dicts == expected_output

    def test_succesful_case2():
        requests.delete(f"{url}/clear/v1")

        new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }
        new_user1 = {"email" : "fakeguy1@gmail.com" , "password": "fake123456","name_first" : "faker", "name_last" : "is_a_faker1" }
        new_user2 = {"email" : "fakeguy2@gmail.com" , "password": "fake123457","name_first" : "faker", "name_last" : "is_a_faker2" }

        response = requests.post(f"{url}/auth/register/v2", json=new_user)
        u_id = response["auth_user_id"]
        owner_token = response["token"]
        response = requests.post(f"{url}/auth/register/v2", json=new_user1)
        u_id1 = response["auth_user_id"]
        input_token = response["token"]
        response = requests.post(f"{url}/auth/register/v2", json=new_user2)
        u_id2 = response["auth_user_id"]

        response = requests.post(f"{BASE_URL}/dm/create/v1", json={ "token" : owner_token, "u_ids" : [u_id1,u_id2] })
        response_data = response.json()
        dm_id = response_data["dm_id"]

        list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : input_token })

        output = list_of_dicts.json()

        expected_output = {"dms" : [{"dm_id" : 1 , 'name': "faker1isafaker , faker1isafaker1 ,fakerisafaker2" }]}

        list_of_dicts = requests.get(f"{url}/dm/list/v1", params={"token" : input_token })

        assert expected_output == list_of_dicts





