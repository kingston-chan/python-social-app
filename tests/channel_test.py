import pytest
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
from src.other import clear_v1
from src.error import InputError, AccessError

# channel_messages_v1 tests

# test - errors
# channel_valid, start_valid, member_valid
def test_ch_mess_error_channel_invalid():
    clear_v1()
    # make user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )
    # no channel created
    # function
    with pytest.raises(InputError):
        channel_messages_v1(user["auth_user_id"], 0, 0)

def test_ch_mess_error_start_invalid():
    clear_v1()
    # make user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )
    # make channel
    ch_id = channels_create_v1(
        user["auth_user_id"],
        "random_channel_name",
        True,
    )
    # function
    with pytest.raises(InputError):
        channel_messages_v1(user["auth_user_id"], ch_id, 100)

def test_ch_mess_error_member_invalid():
    clear_v1()
    # make user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )
    # make channel
    ch_id = channels_create_v1(
        user["auth_user_id"],
        "random_channel_name",
        True,
    )
    # function
    with pytest.raises(AccessError):
        channel_messages_v1((user["auth_user_id"] + 1), ch_id, 0)

# test - valid scenarios
def test_ch_mess():
    clear_v1()
    # make user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )
    # make channel
    ch_id = channels_create_v1(
        user["auth_user_id"],
        "random_channel_name",
        True,
    )
    # function
    assert channel_messages_v1(user["auth_user_id"], ch_id, 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }