import requests, pytest

BASE_URL = 'http://127.0.0.1:8080'

@pytest.fixture
def clear_and_register():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_info = {
        "email": "random@gmail.com", 
        "password": "123abc!@#", 
        "name_first": "John", 
        "name_last": "Smith"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_info)
    response_data = response.json()
    return response_data['token']

# ==== Tests with correct input ==== #

# List channels authorised user is in
def test_user_list_channel(clear_and_register):
    user_token = clear_and_register

    channel_info = {
        "token": user_token, 
        "name": "channel1", 
        "is_public": "True"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response_data = response.json()
    channel1_id = response_data["channel_id"]

    channel_info["name"] = "channel2"
    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response_data = response.json()
    channel2_id = response_data["channel_id"]

    response = requests.get(f"{BASE_URL}/channels/list/v2", json={ "token": user_token })
    response_data = response.json()
    assert len(response_data["channels"]) == 2
    assert response_data["channels"][0]["channel_id"] == channel1_id
    assert response_data["channels"][1]["channel_id"] == channel2_id

# List only channels authorised user is in, including private ones
def test_only_list_authorised_user_channels(clear_and_register):
    user_token1 = clear_and_register

    user_info2 = {
        "email": "random2@gmail.com", 
        "password": "123abc!@#", 
        "name_first": "Bob", 
        "name_last": "Smith"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_info2)
    response_data = response.json()
    user_token2 = response_data['token']

    channel_info = {
        "token": user_token1, 
        "name": "channel1", 
        "is_public": "False"
    }

    response = requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)
    response_data = response.json()
    channel1_id = response_data["channel_id"]

    channel_info["token"] = user_token2
    channel_info["name"] = "channel2"

    requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info)

    response = requests.get(f"{BASE_URL}/channels/list/v2", json={ "token": user_token1 })
    response_data = response.json()
    assert len(response_data["channels"]) == 1
    assert response_data["channels"][0]["channel_id"] == channel1_id


# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.get(f"{BASE_URL}/channels/list/v2", json={ "token": "invalidtoken" })
    assert response.status_code == 400




