import pytest
from tests.route_helpers import auth_logout, auth_register, channel_leave, channels_create, channels_list, channels_listall, clear 

@pytest.fixture
def clear_and_register():
    clear()
    return auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()["token"]

# ==== Tests with correct input ==== #

# Owner is able to leave the channel, but channel still exists, even with no members
def test_owner_leaves_channel_still_exists(clear_and_register):
    channel1_id = channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    
    channel_leave(clear_and_register, channel1_id)
    
    response_data = channels_list(clear_and_register).json()
    assert len(response_data["channels"]) == 0
    
    response_data = channels_listall(clear_and_register).json()
    assert len(response_data["channels"]) == 1

# ==== Tests with incorrect/invalid input ==== #

# Invalid token, but valid channel id
def test_invalid_token(clear_and_register):
    channel1_id = channels_create(clear_and_register, "channel1", True)
    response = channel_leave("invalidtoken", channel1_id)
    assert response.status_code == 403

# Valid token but invalid channel id
def test_invalid_channel_id(clear_and_register):
    response = channel_leave(clear_and_register, 1)
    assert response == 400

# Valid token and channel_id but token's payload contains unauthorised id i.e. not a member of channel
def test_unauthorised_id(clear_and_register):
    channel1_id = channels_create(clear_and_register, "channel1", True)
    user2_token = auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["token"]
    response = channel_leave(user2_token, channel1_id)
    assert response.status_code == 403

# Invalid session
# def test_invalid_session(clear_and_register):
#     channel1_id = channels_create(clear_and_register, "channel1", True)
#     auth_logout(clear_and_register)
#     response = channel_leave(clear_and_register, channel1_id)
#     assert response.status_code == 403

