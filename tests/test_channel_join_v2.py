import pytest
import requests
import json
from src import config
from src.config import port

BASE_URL = 'http://127.0.0.1:' + str(port)


def test_invalid_channel_id():
    requests.delete(f"{BASE_URL}/clear/v1") 

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_laker" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]

    channel_data = {"token" : new_user_token, "name" : "joshuasucks", "is_public": True} 

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_data)

    response_data = response.json()

    invalid_channel_id = response_data["channel_id"] + 1

    response = requests.post(f"{BASE_URL}/channel/join/v2", json={"token": new_user_token, "channel_id": invalid_channel_id})

    assert response.status_code == 400

def test_invalid_token():
    requests.delete(f"{BASE_URL}/clear/v1")
    
    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_laker" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]
    
    channel_data = {"token" : new_user_token, "name" : "joshuasucks", "is_public": "True"} 

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = channel_data)

    invalid_token = "joshsucks"

    channel_id = response.json()["channel_id"]

    response = requests.post(f"{BASE_URL}/channel/join/v2", json={"token": invalid_token, "channel_id": channel_id})

    
    assert response.status_code == 403    

def test_already_a_member():
    requests.delete(f"{BASE_URL}/clear/v1")
     
    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_laker" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]
    
    channel_data = {"token" : new_user_token, "name" : "joshuasucks", "is_public": "True"} 

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = channel_data)

    channel_id = response.json()["channel_id"]

    response = requests.post(f"{BASE_URL}/channel/join/v2", json={"token": new_user_token, "channel_id": channel_id})

    assert response.status_code == 400   

def test_channel_is_private():
    requests.delete(f"{BASE_URL}/clear/v1")
    
    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_laker" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = new_user) 
    response_data = response.json()
    new_user_token = response_data["token"]
    
    channel_data = {"token" : new_user_token, "name" : "joshuaforprez", "is_public": False} 

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = channel_data)
    channel_id = response.json()["channel_id"]
    new_user1 = {"email" : "joshcruzadosucks2@gmail.com" , "password": "joshforprez2","name_first" : "josh4", "name_last" : "president" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = new_user1) 
    response_data = response.json()
    new_user_token1 = response_data["token"]


    response = requests.post(f"{BASE_URL}/channel/join/v2", json={"token": new_user_token1, "channel_id": channel_id})

    assert response.status_code == 403   

 






