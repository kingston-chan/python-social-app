import pytest
import tests.route_helpers as rh

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()["token"]

# ==== Tests with correct input ==== #

# Owner is able to leave the channel, but channel still exists, even with no members
def test_owner_leaves_channel_still_exists(clear_and_register):
    channel1_id = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    user2_token = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["token"]
    rh.channels_create(user2_token, "channel2", True)
    
    rh.channel_leave(clear_and_register, channel1_id)
    
    response_data = rh.channels_list(clear_and_register).json()
    assert len(response_data["channels"]) == 0
    
    response_data = rh.channels_listall(clear_and_register).json()
    assert len(response_data["channels"]) == 2

    rh.channel_join(user2_token, channel1_id)
    channel1_details = rh.channel_details(user2_token, channel1_id)

    assert len(channel1_details.json()["all_members"]) == 1
    assert len(channel1_details.json()["owner_members"]) == 0

# Successfully join and leave channel with stream members
def test_join_and_leave(clear_and_register):
    user2_token = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["token"]
    channel1_id = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    rh.channel_join(user2_token, channel1_id)
    rh.channel_leave(user2_token, channel1_id)
    assert len(rh.channels_list(user2_token).json()["channels"]) == 0
    assert len(rh.channels_listall(user2_token).json()["channels"]) == 1


# ==== Tests with incorrect/invalid input ==== #

# Invalid token, but valid channel id
def test_invalid_token(clear_and_register):
    channel1_id = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    response = rh.channel_leave("invalidtoken", channel1_id)
    assert response.status_code == 403

# Valid token but invalid channel id
def test_invalid_channel_id(clear_and_register):
    channel1_id = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    response = rh.channel_leave(clear_and_register, channel1_id + 1)
    assert response.status_code == 400

# Valid token and channel_id but token's payload contains unauthorised id i.e. not a member of channel
def test_unauthorised_id(clear_and_register):
    channel1_id = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    user2_token = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["token"]
    response = rh.channel_leave(user2_token, channel1_id)
    assert response.status_code == 403

# Invalid session
def test_invalid_session(clear_and_register):
    channel1_id = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    rh.auth_logout(clear_and_register)
    response = rh.channel_leave(clear_and_register, channel1_id)
    assert response.status_code == 403

