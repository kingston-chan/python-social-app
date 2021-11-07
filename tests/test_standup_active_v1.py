import pytest
import tests.route_helpers as rh
import time

@pytest.fixture
def clear():
    return rh.clear()

@pytest.fixture
def first_user_data():
    response = rh.auth_register("email@email.com", "password", "userOne", "lastOne")
    return response.json()

@pytest.fixture
def second_user_data():
    response = rh.auth_register("email2@email.com", "password", "userTwo", "lastTwo")
    return response.json()  

@pytest.fixture
def third_user_data():
    response = rh.auth_register("email3@email.com", "password", "userThree", "lastThree")
    return response.json()

def test_standup_active_member_not_apart_of_channel(clear, first_user_data, second_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]


    response = rh.standup_active(second_user_data["token"], channel_1)

    assert response.status_code == 403


def test_standup_active_invalid_channel_id(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)

    fake_channel_id = "foajsfsaf"

    response = rh.standup_active(first_user_data["token"], fake_channel_id)

    assert response.status_code == 400

def test_standup_active_negative_channel_id(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)

    fake_channel_id = -1

    response = rh.standup_active(first_user_data["token"], fake_channel_id)

    assert response.status_code == 400


def test_standup_active_valid(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    rh.standup_start(first_user_data["token"], channel_1, 5)
    current_time = time.time()

    response = rh.standup_active(first_user_data["token"], channel_1)
    response_data = response.json()
    
    
    assert response.status_code == 200
    assert response_data["is_active"] == True
    assert response_data["time_finish"] >= current_time + 3 and response_data["time_finish"] <= current_time + 7

    


    