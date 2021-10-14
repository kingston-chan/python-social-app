import pytest
import requests
import json
from src import config

BASE_URL = 'http://127.0.0.1:2333'

#400 ======> input error 
#403 ======> access error
def test_invalid_channel_id():
    requests.delete(f"{BASE_URL}/clear/v1")
    #clears any and all information 
    new_user = {"email" : "joshcruzadosucks@gmail.com" , "password": "joshsucks","name_first" : "josh", "name_last" : "sucks" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = user_data) #<---------------equivalent to calling auth register function in iteration 1, and you input the input in the form of json 
    response_data = response.json()#<---------------puts the above function in a dictionary (json form)
    new_user_token = response_data["token"]

    channel_data = {"token" : new_user_token, "name" : "joshuasucks", "is_public": "True"} 

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = channel_data)

    invalid_channel_id = response["channel_id"] + 1

    response = requests.get(f"{BASE_URL}/channel/join/v2", params={"token": new_user_token, "channel_id": invalid_id})

    assert response.status_code == 400

def test_invalid_token():
    requests.delete(f"{BASE_URL}/clear/v1")
    #clears any and all information 
    new_user = {"email" : "joshcruzadosucks@gmail.com" , "password": "joshsucks","name_first" : "josh", "name_last" : "sucks" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = user_data) #<---------------equivalent to calling auth register function in iteration 1, and you input the input in the form of json 
    response_data = response.json()#<---------------puts the above function in a dictionary (json form)
    new_user_token = response_data["token"]
    
    channel_data = {"token" : new_user_token, "name" : "joshuasucks", "is_public": "True"} 

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = channel_data)

    invalid_token = "joshsucks"

    channel_id = response["channel_id"]

    response = requests.get(f"{BASE_URL}/channel/join/v2", params={"token": invalid_token, "channel_id": channel_id})

    assert response.status_code == 403    

def test_already_a_member():
    requests.delete(f"{BASE_URL}/clear/v1")
    #clears any and all information 
    new_user = {"email" : "joshcruzadosucks@gmail.com" , "password": "joshsucks","name_first" : "josh", "name_last" : "sucks" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = user_data) #<---------------equivalent to calling auth register function in iteration 1, and you input the input in the form of json 
    response_data = response.json()#<---------------puts the above function in a dictionary (json form)
    new_user_token = response_data["token"]
    
    channel_data = {"token" : new_user_token, "name" : "joshuasucks", "is_public": "True"} 

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = channel_data)

    channel_id = response["channel_id"]

    response = requests.get(f"{BASE_URL}/channel/join/v2", params={"token": new_user_token, "channel_id": channel_id})

    assert response.status_code == 400   
       
def test_channel_is_private():
    requests.delete(f"{BASE_URL}/clear/v1")
    #clears any and all information 
    new_user = {"email" : "joshcruzadosucks@gmail.com" , "password": "joshsucks","name_first" : "josh", "name_last" : "sucks" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = user_data) #<---------------equivalent to calling auth register function in iteration 1, and you input the input in the form of json 
    response_data = response.json()#<---------------puts the above function in a dictionary (json form)
    new_user_token = response_data["token"]
    
    channel_data = {"token" : new_user_token, "name" : "joshuasucks", "is_public": "False"} 

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = channel_data)
    channel_id = response["channel_id"]
    new_user1 = {"email" : "joshcruzadosucks2@gmail.com" , "password": "joshsucks2","name_first" : "josh2", "name_last" : "sucks2" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = user_data) #<---------------equivalent to calling auth register function in iteration 1, and you input the input in the form of json 
    response_data = response.json()#<---------------puts the above function in a dictionary (json form)
    new_user_token1 = response_data["token"]


    response = requests.get(f"{BASE_URL}/channel/join/v2", params={"token": new_user_token1, "channel_id": channel_id})

    assert response.status_code == 403   

 






