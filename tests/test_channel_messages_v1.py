import pytest
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
from src.other import clear_v1
from src.error import InputError, AccessError


# channel_messages_v1 tests

# test fixtures
@pytest.fixture
def clear_and_create_user1():
    clear_v1()
    user = auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword",
        "fakefirstname",
        "fakelastname",
    )
    return user['auth_user_id']

@pytest.fixture
def create_user2():
    user = auth_register_v1(
        "fakeguytwo@fakeemail.com",
        "fakepasswordtwo",
        "fakefirstnametwo",
        "fakelastnametwo",
    )
    return user['auth_user_id']

# helper functions
def create_channel1(user):
    channel = channels_create_v1(
        user,
        "random_channel_name1",
        True,
    )
    return channel

def create_channel2(user):
    channel = channels_create_v1(
        user,
        "random_channel_name2",
        False,
    )
    return channel

# tests - errors
def test_ch_mess_error_channel_invalid(clear_and_create_user1):
    # no channel created
    user = clear_and_create_user1
    # raise error
    with pytest.raises(InputError):
        channel_messages_v1(user, 1, 0)

def test_correct_channels(clear_and_create_user1):
    user = clear_and_create_user1
    channel = create_channel1(user)
    # raise error
    with pytest.raises(InputError):
        channel_messages_v1(user, channel['channel_id'], 100)

def test_ch_mess_error_member_invalid(clear_and_create_user1, create_user2):
    # raise error
    user1 = clear_and_create_user1
    user2 = create_user2
    channel1 = create_channel1(user1)
    with pytest.raises(AccessError):
        channel_messages_v1(user2, channel1['channel_id'], 0)

def test_ch_mess_error_member_invalid2(clear_and_create_user1, create_user2):
    user1 = clear_and_create_user1
    user2 = create_user2
    channel1 = create_channel1(user1)
    channel2 = create_channel2(user2)
    # raise errors
    with pytest.raises(AccessError):
        channel_messages_v1(user1, channel2['channel_id'], 0)

    with pytest.raises(AccessError):
        channel_messages_v1(user2, channel1['channel_id'], 0)

# test - valid scenarios
def test_ch_mess_public_channel(clear_and_create_user1):
    user1 = clear_and_create_user1
    channel1 = create_channel1(user1)
    # assert
    assert channel_messages_v1(user1, channel1['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

def test_ch_mess_private_channel(clear_and_create_user1, create_user2):
    user1 = clear_and_create_user1
    user2 = create_user2
    create_channel1(user1)
    channel2 = create_channel2(user2)
    # assert
    assert channel_messages_v1(user2, channel2['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

def test_ch_mess_multiple_channels(clear_and_create_user1):
    user1 = clear_and_create_user1
    channel1 = create_channel1(user1)
    channel2 = create_channel2(user1)

    # assert
    assert channel_messages_v1(user1, channel1['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

    assert channel_messages_v1(user1, channel2['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }
