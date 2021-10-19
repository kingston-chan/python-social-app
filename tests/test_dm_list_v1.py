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

    #list_of_dicts = {dm_id , name}
    #dm_details(dm_id) = {name, members}


    list_of_dicts = list_of_dicts.json()
    print (list_of_dicts)
    created_dict = list_of_dicts["dms"][0]
    print(created_dict)
    created_dm_id = created_dict["dm_id"]

    


    response = requests.get(f"{BASE_URL}/dm/details/v1", params={"token": input_token,"dm_id" : created_dm_id})

    response_data = response.json()
    print(response_data)
    if u_id not in response_data["members"]:
        i = False

    assert i  == True
    



