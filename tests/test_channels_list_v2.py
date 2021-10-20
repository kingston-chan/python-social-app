import pytest
import tests.route_helpers as rh

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()['token']


# ==== Tests with correct input ==== #

# List channels authorised user is in
def test_user_list_channel(clear_and_register):
    channel1_id = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    channel2_id = rh.channels_create(clear_and_register, "channel2", True).json()["channel_id"]

    list_channels = rh.channels_list(clear_and_register).json()["channels"]
    
    assert len(list_channels) == 2
    assert list_channels[0]["channel_id"] == channel1_id
    assert list_channels[1]["channel_id"] == channel2_id

# List only channels authorised user is in, including private ones
def test_only_list_authorised_user_channels(clear_and_register):
    user_token2 = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()['token']

    channel1_id = rh.channels_create(clear_and_register, "channel1", False).json()["channel_id"]

    rh.channels_create(user_token2, "Channel2", True)

    list_channels = rh.channels_list(clear_and_register).json()["channels"]
    assert len(list_channels) == 1
    assert list_channels[0]["channel_id"] == channel1_id

# Empty list if user is not in any channels
def test_user_not_in_any_channels(clear_and_register):
    list_channels = rh.channels_list(clear_and_register).json()["channels"]
    assert len(list_channels) == 0
    assert list_channels == []

# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    response = rh.channels_list("invalidtoken")
    assert response.status_code == 403

# Invalid session
def test_invalid_session(clear_and_register):
    rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    rh.auth_logout(clear_and_register)
    response = rh.channels_list(clear_and_register)
    assert response.status_code == 403
    

