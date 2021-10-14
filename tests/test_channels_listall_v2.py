import requests
import pytest

BASE_URL = "http://127.0.0.1:8080"

def test_listall_private_channels():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()
    user_token = response_data["token"]

    channel_1_info = {
        "token": user_token,
        "name": "channel_1",
        "is_public": "False"
    }

    channel_2_info = {
        "token": user_token,
        "name": "channel_2",
        "is_public": "False"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_2_info)
    response_data = response.json()
    channel_2 = response_data["channel_id"]

    response = requests.get(f"{BASE_URL}/channels/listall/v2", params={"token": user_token})
    response_data = response.json()
    
    expected_info = {
        "channels": [channel_1, channel_2],
    }

    assert response_data == expected_info

def test_listall_public_channels():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()
    user_token = response_data["token"]

    channel_1_info = {
        "token": user_token,
        "name": "channel_1",
        "is_public": "True"
    }

    channel_2_info = {
        "token": user_token,
        "name": "channel_2",
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_2_info)
    response_data = response.json()
    channel_2 = response_data["channel_id"]

    response = requests.get(f"{BASE_URL}/channels/listall/v2", params={"token": user_token})
    response_data = response.json()
    
    expected_info = {
        "channels": [channel_1, channel_2],
    }

    assert response_data == expected_info

def test_listall_private_and_public_channels():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()
    user_token = response_data["token"]

    channel_1_info = {
        "token": user_token,
        "name": "channel_1",
        "is_public": "True"
    }

    channel_2_info = {
        "token": user_token,
        "name": "channel_2",
        "is_public": "False"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_2_info)
    response_data = response.json()
    channel_2 = response_data["channel_id"]

    response = requests.get(f"{BASE_URL}/channels/listall/v2", params={"token": user_token})
    response_data = response.json()
    
    expected_info = {
        "channels": [channel_1, channel_2],
    }
    
    assert response_data == expected_info

def test_unauthorised_token():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "keefe@gmail.com",
        "password": "password",
        "name_first": "keefe",
        "name_last": "vuong"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()
    user_token = response_data["token"]

    channel_1_info = {
        "token": user_token,
        "name": "channel_1",
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_1_info)

    response = requests.get(f"{BASE_URL}/channels/listall/v2", params={"token": "oiasjfoaifj"})
    assert response.status_code == 403