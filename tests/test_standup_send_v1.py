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

def test_standup_send_member_not_apart_of_channel(clear, first_user_data, second_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.standup_send(second_user_data["token"], channel_1, "message")

    assert response.status_code == 403


def test_standup_send_invalid_channel_id(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)

    fake_channel_id = "foajsfsaf"

    response = rh.standup_send(first_user_data["token"], fake_channel_id, "message")

    assert response.status_code == 400


def test_standup_send_thousand_characters(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.standup_send(first_user_data["token"], channel_1, "a"*1001)

    assert response.status_code == 400

def test_standup_send_not_active(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.standup_send(first_user_data["token"], channel_1, "message")

    assert response.status_code == 400


def test_standup_send_valid(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    rh.standup_start(first_user_data["token"], channel_1, 5)
    response = rh.standup_send(first_user_data["token"], channel_1, "message")
    
    assert response.status_code == 200
    
def test_standup_send_valid(clear, first_user_data):
    rh.channels_create(first_user_data["token"], "channel_1", True)
    response = rh.channels_create(first_user_data["token"], "channel_2", True)
    channel_2 = response.json()["channel_id"]

    rh.standup_start(first_user_data["token"], channel_2, 5)
    response = rh.standup_send(first_user_data["token"], channel_2, "message")
    
    assert response.status_code == 200
    


    