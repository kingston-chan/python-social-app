import pytest
import time
import tests.route_helpers as rh

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

def test_message_sendlaterdm_member_not_apart_of_dm(clear, first_user_data, second_user_data):
    response = rh.dm_create(first_user_data["token"], [])
    dm_id = response.json()["dm_id"]

    response = rh.message_sendlaterdm(second_user_data["token"], dm_id, "Hello", time.time() + 5)

    assert response.status_code == 403

def test_message_sendlaterdm_unauthorised_token(clear, first_user_data):
    response = rh.dm_create(first_user_data["token"], [])
    dm_id = response.json()["dm_id"]

    fake_user_token = "faiosjfafs"

    response = rh.message_sendlaterdm(fake_user_token, dm_id, "Hello", time.time() + 5)

    assert response.status_code == 403

def test_message_sendlaterdm_invalid_dm_id(clear, first_user_data):
    rh.dm_create(first_user_data["token"], [])

    fake_dm_id = 9999

    response = rh.message_sendlaterdm(first_user_data["token"], fake_dm_id, "Hello", time.time() + 5)

    assert response.status_code == 400

def test_message_sendlaterdm_message_too_long(clear, first_user_data):
    response = rh.dm_create(first_user_data["token"], [])
    dm_id = response.json()["dm_id"]

    long_message = "F"*1001

    response = rh.message_sendlaterdm(first_user_data["token"], dm_id, long_message, time.time() + 5)

    assert response.status_code == 400

def test_message_sendlaterdm_time_in_the_past(clear, first_user_data):
    response = rh.dm_create(first_user_data["token"], [])
    dm_id = response.json()["dm_id"]

    fake_time = time.time() - 300

    response = rh.message_sendlaterdm(first_user_data["token"], dm_id, "Hello", fake_time)

    assert response.status_code == 400

def test_message_sendlaterdm_valid(clear, first_user_data):
    response = rh.dm_create(first_user_data["token"], [])
    dm_id = response.json()["dm_id"]

    response = rh.message_sendlaterdm(first_user_data["token"], dm_id, "Hello", time.time() + 1)

    assert response.status_code == 200

    time.sleep(2)

    response = rh.dm_messages(first_user_data["token"], dm_id, 0)
    messages = response.json()["messages"][0]["message"]

    assert messages == "Hello"





