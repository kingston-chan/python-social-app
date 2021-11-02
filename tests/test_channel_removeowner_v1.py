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


def test_removeowner_globalowner(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(second_user_data["token"], channel_1)

    response = rh.channel_addowner(first_user_data["token"], channel_1, second_user_data["auth_user_id"])

    response = rh.channel_removeowner(first_user_data["token"], channel_1, first_user_data["auth_user_id"])

    response = rh.channel_addowner(first_user_data["token"], channel_1, first_user_data["auth_user_id"])

    assert response.status_code == 200
    

def test_removeowner_valid(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(second_user_data["token"], channel_1)

    response = rh.channel_addowner(first_user_data["token"], channel_1, second_user_data["auth_user_id"])

    response = rh.channel_removeowner(first_user_data["token"], channel_1, second_user_data["auth_user_id"])

    response = rh.channel_details(second_user_data["token"], channel_1)
    response_data = response.json()

    assert response_data["owner_members"][0]["u_id"] == first_user_data["auth_user_id"]

def test_removeowner_invalid_channel_id(clear, first_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)

    fake_channel_id = 9999

    response = rh.channel_removeowner(first_user_data["token"], fake_channel_id, first_user_data["auth_user_id"])
    
    assert response.status_code == 400

def tests_removeowner_no_more_owners(clear, first_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_removeowner(first_user_data["token"], channel_1, first_user_data["auth_user_id"])
    
    assert response.status_code == 400

def test_removeowner_invalid_user_id(clear, first_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    fake_user_id = 9999

    response = rh.channel_removeowner(first_user_data["token"], channel_1, fake_user_id)
    
    assert response.status_code == 400

def tests_removeowner_unauthorised_owner(clear, first_user_data, second_user_data, third_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(third_user_data["token"], channel_1)

    response = rh.channel_join(second_user_data["token"], channel_1)

    response = rh.channel_addowner(first_user_data["token"], channel_1, third_user_data["auth_user_id"])

    response = rh.channel_removeowner(second_user_data["token"], channel_1, first_user_data["auth_user_id"])
    
    assert response.status_code == 403

def tests_removeowner_thats_not_an_owner(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(second_user_data["token"], channel_1)

    response = rh.channel_removeowner(first_user_data["token"], channel_1, second_user_data["auth_user_id"])
    
    assert response.status_code == 400

def test_removeowner_unauthorised_token(clear, first_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    fake_token = "aosfjaoifsjiasfoa"

    response = rh.channel_removeowner(fake_token, channel_1, first_user_data["auth_user_id"])
    
    assert response.status_code == 403

def test_removeowner_global_owner(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_join(second_user_data["token"], channel_1)

    response = rh.channel_removeowner(second_user_data["token"], channel_1, first_user_data["auth_user_id"])

    assert response.status_code == 403

def test_removeowner_non_member_cannot_remove_owner(clear, first_user_data, second_user_data):

    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    response_data = response.json()
    channel_1 = response_data["channel_id"]

    response = rh.channel_removeowner(second_user_data["token"], channel_1, first_user_data["auth_user_id"])

    assert response.status_code == 403
