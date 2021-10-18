import pytest
import tests.route_helpers as rh

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()["token"]

# ==== Tests with correct input ==== #

# Creates a channel successfully
def test_can_create_channel(clear_and_register):
    response = rh.channels_create(clear_and_register, "channel1", True)
    assert response.status_code == 200

    channel1_id = response.json()['channel_id']

    user1_channels = rh.channels_list(clear_and_register).json()["channels"]
    
    assert user1_channels[0]["channel_id"] == channel1_id
    assert user1_channels[0]["name"] == "channel1"

# Created channel must be either private or public 
def test_channel_private_public(clear_and_register):
    channel1 = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    channel2 = rh.channels_create(clear_and_register, "channel2", False).json()["channel_id"]
    channel_details1 = rh.channel_details(clear_and_register, channel1).json()
    channel_details2 = rh.channel_details(clear_and_register, channel2).json()
    assert channel_details1['is_public'] == True
    assert channel_details2['is_public'] == False

# User who creates the channel is channel owner and member (automatically joins), 
# Channel can also have multiple owners and members
def test_channel_owner(clear_and_register):
    user2 = rh.auth_register("random2@gmail.com", "123abc!@#", "Jane", "Smith").json()["token"]
    channel1 = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    rh.channel_join(user2, channel1)
    channel_details = rh.channel_details(clear_and_register, channel1).json()
    assert len(channel_details["owner_members"]) == 1
    assert len(channel_details["all_members"]) == 2


# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    rh.clear()
    response = rh.channels_create("invalid_token", "channel1", True)
    assert response.status_code == 403

# Invalid name (less than 1 character, more than 20 characters)
def test_invalid_name(clear_and_register):
    response = rh.channels_create(clear_and_register, "", True)
    assert response.status_code == 400

    response = rh.channels_create(clear_and_register, "morethantwentycharacters", True)
    assert response.status_code == 400

    response = rh.channels_create(clear_and_register, "                    ", True)
    assert response.status_code == 400

# Channel name already exists
def test_channel_name_already_exists(clear_and_register):
    rh.channels_create(clear_and_register, "channel1", True)
    response = rh.channels_create(clear_and_register, "channel1", True)
    assert response.status_code == 400

    response = rh.channels_create(clear_and_register, "CHANNEL1", True)
    assert response.status_code == 400

    response = rh.channels_create(clear_and_register, "     CHannEL1     ", True)
    assert response.status_code == 400

#Invalid session id
def test_invalid_session(clear_and_register):
    rh.auth_logout(clear_and_register)
    response = rh.channels_create(clear_and_register, "channel1", True)
    assert response.status_code == 403