import pytest

from src.channels import channels_create_v1, channels_list_v1
from src.channel import channel_details_v1
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def clear_and_register_user():
    clear_v1()
    auth_id = auth_register_v1("random@gmail.com", "123abc!@#", "John", "Smith")
    return auth_id

# Channels_create_v1 returns correct channel_id
# def test_returns_channel_id(clear_and_register_user):
#     channel_id = channels_create_v1(auth_id['auth_user_id'], "newchannel", True)
#     channel_list = channels_list_v1(auth_id['auth_user_id'])
#     assert channel_list['channels'][0]['id'] == channel_id['channel_id']  

# Created channel contains a list for channel members
# def test_channel_members(clear_and_register_user):
#     channel_id = channels_create_v1(auth_id['auth_user_id'], "channel1", True)
#     channel_details = channel_details_v1(auth_id['auth_user_id'], channel_id)
#     assert type(channel_details['all_members']) == "list"

# Created channel must be either private or public 
# def test_channel_private_public():
#     clear_v1()
#     auth_id = auth_register_v1("random@gmail.com", "123abc!@#", "John", "Smith")
#     channel_id1 = channels_create_v1(auth_id['auth_user_id'], "channel1", True)
#     channel_id2 = channels_create_v1(auth_id['auth_user_id'], "channel2", False)
#     channel_details1 = channel_details_v1(auth_id['auth_user_id'], channel_id1)
#     channel_details2 = channel_details_v1(auth_id['auth_user_id'], channel_id2)
#     assert channel_details1['is_public'] == True
#     assert channel_details2['is_public'] == False

# User who creates the channel is channel owner and member (automatically joins), 
# Channel can also have multiple owners and members
# def test_channel_owner(clear_and_register_user):
#     auth_id = clear_and_register_user
#     channel_id = channels_create_v1(auth_id['auth_user_id'], "channel1", True)
#     channel_details = channel_details_v1(auth_id['auth_user_id'], channel_id)
#     assert auth_id['auth_user_id'] in channel_details['owner_members']
#     assert auth_id['auth_user_id'] in channel_details['all_members']
#     assert type(channel_details["owner_members"]) == "list"
#     assert type(channel_details["all_members"]) == "list"

# InputError when: length of name is less than 1 or more than 20 characters
def test_invalid_channel_name(clear_and_register_user):
    auth_id = clear_and_register_user
    with pytest.raises(InputError):
        channels_create_v1(auth_id['auth_user_id'], "", True)
        channels_create_v1(auth_id['auth_user_id'], "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", True)

# Cannot create a channel with same name
def test_channel_same_name(clear_and_register_user):
    auth_id = clear_and_register_user
    channels_create_v1(auth_id['auth_user_id'], "channel1", True)
    with pytest.raises(InputError):
        channels_create_v1(auth_id['auth_user_id'], "Channel1", True)

# Auth_user_id must be valid, user must exist
def test_invalid_auth_user_id(clear_and_register_user):
    auth_id = clear_and_register_user
    with pytest.raises(AccessError):
        channels_create_v1(auth_id['auth_user_id']+1, "channel2", False)

# Channel stores messages
# def test_channel_members(clear_and_register_user):
#     auth_id = clear_and_register_user
#     channel_id = channels_create_v1(auth_id['auth_user_id'], "channel1", True)
#     channel_details = channel_details_v1(auth_id['auth_user_id'], channel_id)
#     assert type(channel_details['messages']) == "list"
