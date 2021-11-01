import pytest
import tests.route_helpers as rh
import time

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

def test_message_sendlater_member_not_apart_of_channel(clear, first_user_data, second_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.message_sendlater(second_user_data["token"], channel_1, "Hello", int(time.time()) + 5)

    assert response.status_code == 403

def test_message_sendlater_unauthorised_user(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    fake_user_token = "foajsfsaf"

    response = rh.message_sendlater(fake_user_token, channel_1, "Hello", int(time.time()) + 5)

    assert response.status_code == 403

def test_message_sendlater_invalid_channel_id(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)

    fake_channel_id = "foajsfsaf"

    response = rh.message_sendlater(first_user_data["token"], fake_channel_id, "Hello", int(time.time()) + 5)

    assert response.status_code == 400

def test_message_sendlater_too_long_message(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    long_message = "F"*1001

    response = rh.message_sendlater(first_user_data["token"], channel_1, long_message, int(time.time()) + 5)

    assert response.status_code == 400

def test_message_sendlater_time_in_the_past(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    time_in_the_past = int(time.time()) - 30

    response = rh.message_sendlater(first_user_data["token"], channel_1, "Hello", time_in_the_past)

    assert response.status_code == 400

def test_message_sendlater_valid(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.message_sendlater(first_user_data["token"], channel_1, "Hello", int(time.time()) + 5)

    assert response.status_code == 200
    assert response.json()["message_id"] == 1

    time.sleep(8)

    response = rh.channel_messages(first_user_data["token"], channel_1, 0)
    response_data = response.json()
    message = response_data["messages"][0]["message"]

    assert message == "Hello"