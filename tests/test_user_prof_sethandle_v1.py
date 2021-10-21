import requests
import pytest
from src.config import url

BASE_URL = url

#400 is input error
#403 is access error

def test_input_string_too_long():
    requests.delete(f"{BASE_URL}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user) 

    response_data = response.json()
    user_token = response_data["token"]
    
    new_handle = "thispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfakethispersonisfake"

    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={"token": user_token, "handle_str": new_handle})

    assert response.status_code == 400

def test_non_alphanumeric_inputs():
    requests.delete(f"{BASE_URL}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user) 

    response_data = response.json()
    user_token = response_data["token"]
    
    new_handle = "***********"

    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={"token": user_token, "handle_str": new_handle})

    assert response.status_code == 400
def test_handle_string_is_used():
    requests.delete(f"{BASE_URL}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user) 
    
    response_data = response.json()
    user_token = response_data["token"]

    new_handle = "thispersonisfake"

    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={"token": user_token, "handle_str": new_handle})

    new_user = {"email" : "fakeguy1@gmail.com" , "password": "fake123451","name_first" : "faker1", "name_last" : "is_a_faker1" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user) 

    response_data = response.json()

    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={"token": user_token, "handle_str": new_handle})
    assert response.status_code == 400

def test_invalid_token():
    requests.delete(f"{BASE_URL}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user) 
    
    new_handle = "thispersonisfake"

    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={"token": 1, "handle_str": new_handle})
    assert response.status_code == 403

def test_succesful_case():
    requests.delete(f"{BASE_URL}/clear/v1")

    new_user = {"email" : "fakeguy@gmail.com" , "password": "fake12345","name_first" : "faker", "name_last" : "is_a_faker" }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=new_user) 

    response_data = response.json()
    user_token = response_data["token"]
    
    new_handle = "thispersonisfake"

    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={"token": user_token, "handle_str": new_handle})
    assert response.status_code == 200
