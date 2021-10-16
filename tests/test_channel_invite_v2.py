import pytest
import requests
import json

from requests.models import Response
from src.config import url


#400 is input error
#403 is access error
def test_invalid_channel():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    auth_user_token = response_data["token"]

    channel_data = {"token" : auth_user_token, "name" : "joshuasucks", "is_public": True} 

    response = requests.post(f"{url}/channels/create/v2", json=channel_data)

    response_data = response.json()

    invalid_channel_id = response_data["channel_id"] + 1

    new_user1 = {"email" : "fakeguy1@gmail.com" , "password": "fake123456","name_first" : "faker1", "name_last" : "is_a_faker1" }
    response = requests.post(f"{url}/auth/register/v2", json=new_user1) 
    response_data = response.json()
    new_user_token = response_data["token"]
    new_user_id = response_data["auth_user_id"]

    response = requests.post(f"{url}/channel/invite/v2", json={"token": auth_user_token, "channel_id": invalid_channel_id, "u_id" : new_user_id})
    

    assert response.status_code == 400

def test_already_member():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    auth_user_token = response_data["token"]
    new_user_id = response_data["auth_user_id"]

    channel_data = {"token" : auth_user_token, "name" : "joshuasucks", "is_public": True} 

    response = requests.post(f"{url}/channels/create/v2", json=channel_data)

    response_data = response.json()

    channel_id = response_data["channel_id"]

    response = requests.post(f"{url}/channel/invite/v2", json={"token": auth_user_token, "channel_id": channel_id, "u_id" : new_user_id})

    assert response.status_code == 400

def test_invalid_user_id():
    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    auth_user_token = response_data["token"]
    new_user_id = response_data["auth_user_id"]
    channel_data = {"token" : auth_user_token, "name" : "joshuasucks", "is_public": True} 

    response = requests.post(f"{url}/channels/create/v2", json=channel_data)

    response_data = response.json()

    channel_id = response_data["channel_id"]

    invalid_u_id = new_user_id + 1

    response = requests.post(f"{url}/channel/invite/v2", json={"token": auth_user_token, "channel_id": channel_id, "u_id" : invalid_u_id})

    assert response.status_code == 400

def test_not_auth_user():

    requests.delete(f"{url}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{url}/auth/register/v2", json=new_user) 
    response_data = response.json()
    auth_user_token = response_data["token"]
    new_user_id = response_data["auth_user_id"]
    channel_data = {"token" : auth_user_token, "name" : "joshuasucks", "is_public": True} 

    response = requests.post(f"{url}/channels/create/v2", json=channel_data)

    response_data = response.json()

    channel_id = response_data["channel_id"]

    invalid_u_id = new_user_id + 1

    response = requests.post(f"{url}/channel/invite/v2", json={"token": invalid_u_id, "channel_id": channel_id, "u_id" : invalid_u_id})

    assert response.status_code == 403
