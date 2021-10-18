import requests
import pytest
from src.config import url

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
