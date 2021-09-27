import pytest

from src.other import clear_v1
from src.channel import channel_details_v1
from src.channel import channel_invite_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.error import AccessError
from src.error import InputError

def test_details_invalid_channel_id():
    clear_v1()
    user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")
    channel_id_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", False)
    invalid_channel_id = 99999
    with pytest.raises(InputError):
        channel_details_v1(user_data['auth_user_id'], invalid_channel_id)

def test_details_uninvited_member():
    clear_v1()
    owner_user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")
    uninvited_user_data = auth_register_v1("eagle@gmail.com", "password", "team", "eagle")
    channel_id_1 = channels_create_v1(owner_user_data['auth_user_id'], "channel_1", False)
    with pytest.raises(AccessError):
        channel_details_v1(uninvited_user_data['auth_user_id'], channel_id_1)

def test_details_valid_channel_id():
    clear_v1()
    user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")
    channel_id_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", False)
    channel_details = {
        "name": "channel_1",
        "is_public": False,
        "owner_members": [
            {
                'id': user_data['auth_user_id'],
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',                
            }
        ],
        "all_members": [{}]
    }
    assert(channel_details_v1(user_data['auth_user_id'], channel_id_1) == channel_details)

def test_details_invited_member():
    clear_v1()
    owner_user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")
    second_user_data = auth_register_v1("eagle@gmail.com", "password", "team", "eagle")
    channel_id_1 = channels_create_v1(owner_user_data['auth_user_id'], "channel_1", False)
    channel_invite_v1(owner_user_data['auth_user_id'], channel_id_1, second_user_data)
    channel_details = {
        "name": "channel_1",
        "is_public": False,
        "owner_members": [
            {
                'id': owner_user_data['auth_user_id'],
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',                
            }
        ],
        "all_members": [
            {
                'id': owner_user_data['auth_user_id'],
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',                
            },
            {
                'id': second_user_data['auth_user_id'],
                'email': 'eagle@gmail.com',
                'name_first': 'team',
                'name_last': 'eagle',
                'handle_str': 'teameagle',                    
            }
        ]
    }
    assert(channel_details_v1(second_user_data['auth_user_id'], channel_id_1) == channel_details)

def test_details_unauthorised_user_data():
    clear_v1()
    user_data = auth_register_v1("keefe@gmail.com", "password", "keefe", "vuong")
    channel_id_1 = channels_create_v1(user_data['auth_user_id'], "channel_1", True)
    fake_user_data = 99999
    with pytest.raises(AccessError):
        channel_details_v1(fake_user_data, channel_id_1)