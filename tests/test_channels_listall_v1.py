import pytest

from src.other import clear_v1
from src.channels import channels_listall_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.error import AccessError

@pytest.fixture
def clear_and_register_user():
    clear_v1()
    return auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")

# Tests that all private channels are listed.
def test_listall_private_channels(clear_and_register_user):
    user_data = clear_and_register_user
    
    channel_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", False)
    channel_2 = channels_create_v1(user_data['auth_user_id'], "channel_2", False)
    channel_3 = channels_create_v1(user_data['auth_user_id'], "channel_3", False)
    channel_4 = channels_create_v1(user_data['auth_user_id'], "channel_4", False)

    channel_1['name'] = "channel_1"
    channel_2['name'] = "channel_2"
    channel_3['name'] = "channel_3"
    channel_4['name'] = "channel_4"

    channel_info = {
        "channels": [channel_1, channel_2, channel_3, channel_4],
    }
    
    assert channels_listall_v1(user_data['auth_user_id']) == channel_info

# Tests that an AccessError is thrown for an unauthorised user
def test_listall_unauthorised_user_data(clear_and_register_user):
    user_data = clear_and_register_user

    channels_create_v1(user_data['auth_user_id'], "channel_1", True)
    channels_create_v1(user_data['auth_user_id'], "channel_2", False)
    channels_create_v1(user_data['auth_user_id'], "channel_3", True)
    channels_create_v1(user_data['auth_user_id'], "channel_4", False)

    fake_user_data = 999999

    with pytest.raises(AccessError):
        channels_listall_v1(fake_user_data)

# Tests that all public channels are listed
def test_listall_public_channels(clear_and_register_user):
    user_data = clear_and_register_user

    channel_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", True)
    channel_2 = channels_create_v1(user_data['auth_user_id'], "channel_2", True)
    channel_3 = channels_create_v1(user_data['auth_user_id'], "channel_3", True)
    channel_4 = channels_create_v1(user_data['auth_user_id'], "channel_4", True)

    channel_1['name'] = "channel_1"
    channel_2['name'] = "channel_2"
    channel_3['name'] = "channel_3"
    channel_4['name'] = "channel_4"

    channel_info = {
        "channels": [channel_1, channel_2, channel_3, channel_4],
    }

    assert channels_listall_v1(user_data['auth_user_id']) == channel_info

# Tests that all public and private channels are listed
def test_listall_public_and_private_channels(clear_and_register_user):
    user_data = clear_and_register_user

    channel_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", True)
    channel_2 = channels_create_v1(user_data['auth_user_id'], "channel_2", True)
    channel_3 = channels_create_v1(user_data['auth_user_id'], "channel_3", False)
    channel_4 = channels_create_v1(user_data['auth_user_id'], "channel_4", False)

    channel_1['name'] = "channel_1"
    channel_2['name'] = "channel_2"
    channel_3['name'] = "channel_3"
    channel_4['name'] = "channel_4"

    channel_info = {
        "channels": [channel_1, channel_2, channel_3, channel_4],
    }

    assert channels_listall_v1(user_data['auth_user_id']) == channel_info

# Tests that no channels are listed if none have been created.
def test_listall_no_channels(clear_and_register_user):
    user_data = clear_and_register_user

    channel_info = {
        "channels": [],
    }

    assert channels_listall_v1(user_data['auth_user_id']) == channel_info