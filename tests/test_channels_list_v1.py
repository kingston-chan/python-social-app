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
    return auth_id['auth_user_id']

# Returns the only channels that the user is in
def test_correct_channels(clear_and_register_user):
    auth_id = clear_and_register_user
    channel1 = channels_create_v1(auth_id, "channel1", True)
    auth2 = auth_register_v1("validemail@gmail.com", "123abc!@#", "Jane", "Smith")
    channels_create_v1(auth2['auth_user_id'], "channel2", True)
    num_channels = 0
    channels_list = channels_list_v1(auth_id)
    for channel in channels_list['channels']:
        num_channels += 1
        assert channel['channel_id'] == channel1['channel_id']
    assert num_channels == 1


# AccessError is thrown when invalid user id is given
def test_invalid_auth_user_id(clear_and_register_user):
    auth_id = clear_and_register_user
    with pytest.raises(AccessError):
        channels_list_v1(auth_id+1)

# Return values are correct i.e. { channel_id, name }
def test_return_values(clear_and_register_user):
    auth_id = clear_and_register_user
    channel1 = channels_create_v1(auth_id, "channel1", True)
    channel_list = channels_list_v1(auth_id)
    assert channel_list['channels'][0]['channel_id'] == channel1['channel_id']
    assert type(channel_list['channels'][0]['channel_id']) is int
    assert channel_list['channels'][0]['name'] == "channel1"
    assert type(channel_list['channels'][0]['name']) is str

# Empty list of channels is returned if user does not belong in any channel
def test_user_not_in_any_channels(clear_and_register_user):
    auth_id = clear_and_register_user
    channel_list = channels_list_v1(auth_id)
    assert channel_list['channels'] == []

# Returns channels that are private that the user is in
def test_return_private_channels_of_user(clear_and_register_user):
    auth_id = clear_and_register_user
    channel1 = channels_create_v1(auth_id, "channel1", False)
    channel_list = channels_list_v1(auth_id)
    assert len(channel_list['channels']) == 1
    assert channel_list['channels'][0]['channel_id'] == channel1['channel_id']
    assert channel_list['channels'][0]['name'] == "channel1"
