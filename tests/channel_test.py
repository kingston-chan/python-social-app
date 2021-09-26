import pytest
from src.auth import auth_register_v1
from src.channel import channel
from src.other import other

# channel_messages_v1 tests
# test - errors
# channel_valid, start_valid, member_valid
def test_ch_mess_error_channel-invalid():
    clear_v1()
    # make user
    auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword"
        "fakefirstname"
        "fakelastname"
    )
    id = auth_login_v1(
        "fakeguy@fakeemail.com"
        "fakepassword"
    )
    # no channel created
    # function
    with pytest.raises(InputError):
        channel_messages_v1(id, 0, 0)

def test_ch_mess_error_start-invalid():
    clear_v1()
    # make user
    auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword"
        "fakefirstname"
        "fakelastname"
    )
    id = auth_login_v1(
        "fakeguy@fakeemail.com"
        "fakepassword"
    )
    # make channel
    ch_id = channels_create(
        id,
        "random_channel_name",
        True
    )
    # function
    with pytest.raises(InputError):
        channel_messages_v1(id, ch_id, 100)

def test_ch_mess_error_member-invalid():
    clear_v1()
    # make user
    auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword"
        "fakefirstname"
        "fakelastname"
    )
    id = auth_login_v1(
        "fakeguy@fakeemail.com"
        "fakepassword"
    )
    # make channel
    ch_id = channels_create(
        id,
        "random_channel_name",
        True
    )
    # function
    with pytest.raises(InputError):
        channel_messages_v1(id + 1, ch_id, 100)

# test - valid scenarios
def test_ch_mess():
    clear_v1()
        clear_v1()
    # make user
    auth_register_v1(
        "fakeguy@fakeemail.com",
        "fakepassword"
        "fakefirstname"
        "fakelastname"
    )
    id = auth_login_v1(
        "fakeguy@fakeemail.com"
        "fakepassword"
    )
    # make channel
    ch_id = channels_create(
        id,
        "random_channel_name",
        True
    )
    # function
    assert channel_messages_v1(id, ch_id, 0) == {
        'messages':
        'start': 0
        'end': -1
    }
    pass