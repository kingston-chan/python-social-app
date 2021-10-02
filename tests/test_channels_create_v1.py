import pytest

from src.channels import channels_create_v1, channels_list_v1
from src.channel import channel_details_v1, channel_join_v1, channel_messages_v1
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def clear_and_register_user():
    clear_v1()
    return auth_register_v1("random@gmail.com", "123abc!@#", "John", "Smith")['auth_user_id']

                #============== Module tests ==============#

# InputError when: length of name is less than 1 or more than 20 characters
def test_invalid_channel_name(clear_and_register_user):
    auth_id = clear_and_register_user
    with pytest.raises(InputError):
        channels_create_v1(auth_id, "", True)
    with pytest.raises(InputError):
        channels_create_v1(auth_id, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", True)

# Cannot create a channel with same name
def test_channel_same_name(clear_and_register_user):
    auth_id = clear_and_register_user
    channels_create_v1(auth_id, "channel1", True)
    with pytest.raises(InputError):
        channels_create_v1(auth_id, "Channel1", True)

# Auth_user_id must be valid, user must exist
def test_invalid_auth_user_id(clear_and_register_user):
    auth_id = clear_and_register_user
    with pytest.raises(AccessError):
        channels_create_v1(auth_id+1, "channel2", False)

# Removes trailing/leading whitespace
def test_whitespace(clear_and_register_user):
    auth_id = clear_and_register_user
    channels_create_v1(auth_id, "      channel1        ", True)
    with pytest.raises(InputError):
        channels_create_v1(auth_id, " chaNNel1     ", False)
    with pytest.raises(InputError):
        channels_create_v1(auth_id, "                      ", False)

                #=========== Integration tests ===========#

# Channels_create_v1 returns correct channel_id
def test_returns_channel_id(clear_and_register_user):
    auth_id = clear_and_register_user  
    newchannel = channels_create_v1(auth_id, "newchannel", True)
    channel_list = channels_list_v1(auth_id)
    assert channel_list['channels'][0]['channel_id'] == newchannel['channel_id']  

# Created channel must be either private or public 
def test_channel_private_public(clear_and_register_user):
    auth_id = clear_and_register_user     
    channel1 = channels_create_v1(auth_id, "channel1", True)
    channel2 = channels_create_v1(auth_id, "channel2", False)
    channel_details1 = channel_details_v1(auth_id, channel1['channel_id'])
    channel_details2 = channel_details_v1(auth_id, channel2['channel_id'])
    assert channel_details1['is_public'] == True
    assert channel_details2['is_public'] == False

# User who creates the channel is channel owner and member (automatically joins), 
# Channel can also have multiple owners and members
def test_channel_owner(clear_and_register_user):
    user1 = clear_and_register_user
    user2 = auth_register_v1("random2@gmail.com", "123abc!@#", "Jane", "Smith")
    channel1 = channels_create_v1(user1, "channel1", True)
    channel_join_v1(user2['auth_user_id'], channel1['channel_id'])
    channel_details = channel_details_v1(user1, channel1['channel_id'])
    assert len(channel_details["owner_members"]) == 1
    assert len(channel_details["all_members"]) == 2
