import pytest
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

def test_message_share_member_not_in_channel(clear, first_user_data, second_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.message_send(first_user_data["token"], channel_1, "hello")
    message_id = response.json()["message_id"]

    response = rh.message_share(second_user_data["token"], message_id, None, channel_1, -1)
    
    assert response.status_code == 403

def test_message_share_member_not_in_dm(clear, first_user_data, second_user_data):
    response = rh.dm_create(first_user_data["token"], [])
    dm_id = response.json()["dm_id"]

    response = rh.message_senddm(first_user_data["token"], dm_id, "hello")
    message_id = response.json()["message_id"]

    response = rh.message_share(second_user_data["token"], message_id, None, -1, dm_id)

    assert response.status_code == 403

def test_message_share_invalid_channel_id(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.message_send(first_user_data["token"], channel_1, "hello")
    message_id = response.json()["message_id"]

    fake_channel_id = 9999

    response = rh.message_share(first_user_data["token"], message_id, None, fake_channel_id, -1)

    assert response.status_code == 400

def test_message_share_invalid_dm_id(clear, first_user_data):
    response = rh.dm_create(first_user_data["token"], [])
    dm_id = response.json()["dm_id"]

    response = rh.message_senddm(first_user_data["token"], dm_id, "hello")
    message_id = response.json()["message_id"]

    fake_dm_id = 9999

    response = rh.message_share(first_user_data["token"], message_id, None, -1, fake_dm_id)

    assert response.status_code == 400

def test_message_share_channel_id_and_dm_id_arent_negative_1(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.dm_create(first_user_data["token"], [])
    dm_id = response.json()["dm_id"]

    response = rh.message_send(first_user_data["token"], channel_1, "hello")
    message_id = response.json()["message_id"]

    response = rh.message_share(first_user_data["token"], message_id, None, channel_1, dm_id)

    assert response.status_code == 400

def test_message_share_channel_og_message_id_not_valid(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.message_send(first_user_data["token"], channel_1, "hello")

    fake_message_id = 9999

    response = rh.message_share(first_user_data["token"], fake_message_id, None, channel_1, -1)

    assert response.status_code == 400

def test_message_share_dm_og_message_id_not_valid(clear, first_user_data):
    response = rh.dm_create(first_user_data["token"], [])
    dm_id = response.json()["dm_id"]

    response = rh.message_senddm(first_user_data["token"], dm_id, "hello")

    fake_message_id = 9999

    response = rh.message_share(first_user_data["token"], fake_message_id, None, -1, dm_id)

    assert response.status_code == 400

def test_message_share_length_of_message_too_long(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.message_send(first_user_data["token"], channel_1, "hello")
    message_id = response.json()["message_id"]

    long_message = "F"*1001

    response = rh.message_share(first_user_data["token"], message_id, long_message, channel_1, -1)

    assert response.status_code == 400

def test_message_share_unauthorised_user(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]

    response = rh.message_send(first_user_data["token"], channel_1, "hello")
    message_id = response.json()["message_id"]

    fake_user_id = 9999

    response = rh.message_share(fake_user_id, message_id, None, channel_1, -1)

    assert response.status_code == 403
