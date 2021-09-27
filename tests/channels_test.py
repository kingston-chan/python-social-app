import pytest

from src.other import clear_v1
from src.channels import channels_listall_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.error import AccessError

def test_listall_private_channels():
    clear_v1()
    user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")
    channel_id_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", False)
    channel_id_2 = channels_create_v1(user_data['auth_user_id'], "channel_2", False)
    channel_id_3 = channels_create_v1(user_data['auth_user_id'], "channel_3", False)
    channel_id_4 = channels_create_v1(user_data['auth_user_id'], "channel 4", False)

    channel_info = {
        "channel_id": [channel_id_1, channel_id_2, channel_id_3, channel_id_4],
        "name": ["channel_1", "channel_2", "channel_3", "channel_4"],
    }

    assert channels_listall_v1(user_data['auth_user_id']) == channel_info

def test_listall_unauthorised_user_data():
    clear_v1()
    user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")
    fake_user_data = 999999
    channel_id_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", True)
    channel_id_2 = channels_create_v1(user_data['auth_user_id'], "channel_2", False)
    channel_id_3 = channels_create_v1(user_data['auth_user_id'], "channel_3", True)
    channel_id_4 = channels_create_v1(user_data['auth_user_id'], "channel 4", False)

    channel_info = {
        "channel_id": [channel_id_1, channel_id_2, channel_id_3, channel_id_4],
        "name": ["channel_1", "channel_2", "channel_3", "channel_4"],
    }

    with pytest.raises(AccessError):
        channels_listall_v1(fake_user_data)

def test_listall_public_channels():
    clear_v1()
    user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")
    channel_id_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", True)
    channel_id_2 = channels_create_v1(user_data['auth_user_id'], "channel_2", True)
    channel_id_3 = channels_create_v1(user_data['auth_user_id'], "channel_3", True)
    channel_id_4 = channels_create_v1(user_data['auth_user_id'], "channel 4", True)

    channel_info = {
        "channel_id": [channel_id_1, channel_id_2, channel_id_3, channel_id_4],
        "name": ["channel_1", "channel_2", "channel_3", "channel_4"],
    }

    assert channels_listall_v1(user_data['auth_user_id']) == channel_info

def test_listall_public_and_private_channels():
    clear_v1()
    user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")
    channel_id_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", True)
    channel_id_2 = channels_create_v1(user_data['auth_user_id'], "channel_2", True)
    channel_id_3 = channels_create_v1(user_data['auth_user_id'], "channel_3", False)
    channel_id_4 = channels_create_v1(user_data['auth_user_id'], "channel_4", False)

    channel_info = {
        "channel_id": [channel_id_1, channel_id_2, channel_id_3, channel_id_4],
        "name": ["channel_1", "channel_2", "channel_3", "channel_4"],
    }

    assert channels_listall_v1(user_data['auth_user_id']) == channel_info

def test_listall_no_channels():
    clear_v1()
    user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")

    assert channels_listall_v1(user_data['auth_user_id']) == {}