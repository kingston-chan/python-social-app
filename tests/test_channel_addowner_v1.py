import pytest
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

@pytest.fixture
def clear():
    return rh.clear()

@pytest.fixture
def first_user_data():
    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    return response.json()

@pytest.fixture
def second_user_data():
    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    return response.json()  

@pytest.fixture
def third_user_data():
    response = rh.auth_register("butcher@gmail.com", "password", "knife", "butcher")
    return response.json()

def test_addowner_valid(clear, first_user_data, second_user_data):

    owner_list = []

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(second_user_data["token"], channel_1)

    response = rh.channel_addowner(first_user_data["token"], channel_1, second_user_data["auth_user_id"])

    response = rh.channel_details(second_user_data["token"], channel_1)
    response_data = response.json()

    owner_list.append(response_data["owner_members"][0]["u_id"])
    owner_list.append(response_data["owner_members"][1]["u_id"])

    expected_outcome = [first_user_data["auth_user_id"], second_user_data["auth_user_id"]]

    assert owner_list == expected_outcome

def test_addowner_invalid_channel_id(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(second_user_data["token"], channel_1)

    fake_channel_id = 9999

    response = rh.channel_addowner(first_user_data["token"], fake_channel_id, second_user_data["auth_user_id"])
    
    assert response.status_code == 400
def test_addowner_invalid_user_id(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(second_user_data["token"], channel_1)

    fake_user_id = 9999

    response = rh.channel_addowner(first_user_data["token"], channel_1, fake_user_id)

    assert response.status_code == 400

def test_addowner_uninvited_member(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_addowner(first_user_data["token"], channel_1, second_user_data["auth_user_id"])

    assert response.status_code == 400

def test_addowner_already_owner(clear, first_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_addowner(first_user_data["token"], channel_1, first_user_data["auth_user_id"])
    
    assert response.status_code == 400

def test_addowner_no_owner_perms(clear, first_user_data, second_user_data, third_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(third_user_data["token"], channel_1)

    response = rh.channel_join(third_user_data["token"], channel_1)

    response = rh.channel_addowner(second_user_data["token"], channel_1, third_user_data["auth_user_id"])

    assert response.status_code == 403

def test_addowner_global_owner(clear, third_user_data, first_user_data):

    owner_list = []

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(third_user_data["token"], channel_1)

    response = rh.channel_addowner(third_user_data["token"], channel_1, third_user_data["auth_user_id"])

    response = rh.channel_details(third_user_data["token"], channel_1)
    response_data = response.json()

    owner_list.append(response_data["owner_members"][0]["u_id"])
    owner_list.append(response_data["owner_members"][1]["u_id"])

    expected_outcome = [third_user_data["auth_user_id"], first_user_data["auth_user_id"]]

    assert owner_list == expected_outcome


def test_addowner_unauthorised_token(clear, first_user_data, third_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    print(response_data)
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(third_user_data["token"], channel_1)

    fake_token = "aoisjfaoisjfja"

    response = rh.channel_addowner(fake_token, channel_1, third_user_data["auth_user_id"])
    
    assert response.status_code == 403