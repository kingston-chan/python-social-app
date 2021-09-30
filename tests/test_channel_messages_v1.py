import pytest
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
from src.other import clear_v1
from src.error import InputError, AccessError

# channel_messages_v1 tests

# test - errors
def test_ch_mess_error_channel_invalid():
    clear_v1()
    # make the user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )
    # no channel created
    # raise error
    with pytest.raises(InputError):
        channel_messages_v1(user['auth_user_id'], 1, 0)

def test_ch_mess_error_start_invalid():
    clear_v1()
     # make the user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )

    # make a channel
    channel = channels_create_v1(
        user['auth_user_id'],
        "random_channel_name",
        True,
    )

    # raise error
    with pytest.raises(InputError):
        channel_messages_v1(user['auth_user_id'], channel['channel_id'], 100)

def test_ch_mess_error_member_invalid():
    clear_v1()
    # make the user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )

    # make a channel
    channel = channels_create_v1(
        user['auth_user_id'],
        "random_channel_name",
        True,
    )
    # make an unauthorised user of the channel
    unauth_user = auth_register_v1(
        "fakeguytwo@fakeemail.com",
        "fakepasswordtwo",
        "fakefirstnametwo",
        "fakesecondlastnametwo",
    )
    # raise error
    with pytest.raises(AccessError):
        channel_messages_v1(unauth_user['auth_user_id'], channel['channel_id'], 0)

def test_ch_mess_error_member_invalid2():
    clear_v1()

    # make 2 users
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )

    user2 = auth_register_v1(
        "fakeguytwo@fakeemail.com",
        "fakepasswordtwo",
        "fakefirstnametwo",
        "fakelastnametwo",
    )

    # make two channels
    channel = channels_create_v1(
        user['auth_user_id'],
        "random_channel_name",
        True,
    )

    channel2 = channels_create_v1(
        user2['auth_user_id'],
        "random_channel_name2",
        True,
    )

    # raise errors
    with pytest.raises(AccessError):
        channel_messages_v1(user['auth_user_id'], channel2['channel_id'], 0)
    with pytest.raises(AccessError):
        channel_messages_v1(user2['auth_user_id'], channel['channel_id'], 0)

# test - valid scenarios
def test_ch_mess_public_channel():
    clear_v1()
    # make the user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )

    # make a channel
    channel = channels_create_v1(
        user['auth_user_id'],
        "random_channel_name",
        True,
    )

    # assert
    assert channel_messages_v1(user['auth_user_id'], channel['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

def test_ch_mess_private_channel():
    clear_v1()
    # make the user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )

    # make a channel
    channel = channels_create_v1(
        user['auth_user_id'],
        "random_channel_name",
        False,
    )

    # assert
    assert channel_messages_v1(user['auth_user_id'], channel['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

def test_ch_mess_multiple_channels():
    clear_v1()
    # make the user
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )

    # make two channel
    channel = channels_create_v1(
        user['auth_user_id'],
        "random_channel_name",
        True,
    )

    channel2 = channels_create_v1(
        user['auth_user_id'],
        "random_channel_name2",
        True,
    )

    # assert
    assert channel_messages_v1(user['auth_user_id'], channel['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

    assert channel_messages_v1(user['auth_user_id'], channel2['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

