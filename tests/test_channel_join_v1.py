import pytest

from src.channel import channel_details_v1, channel_join_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def clear_and_register():
    clear_v1()
    return auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname")['auth_user_id']

@pytest.fixture
def create_public_channel(clear_and_register):
    return channels_create_v1(clear_and_register, "random_channel_name", True)['channel_id']        

@pytest.fixture
def create_private_channel(clear_and_register):
    return channels_create_v1(clear_and_register, "random_channel_name", False)['channel_id']

def test_invalid_user(clear_and_register, create_public_channel):
    with pytest.raises(AccessError):
        channel_join_v1(clear_and_register+1, create_public_channel)         

def test_already_member(clear_and_register, create_public_channel):
    # Creator of channel is already in channel      
    with pytest.raises(InputError):
        channel_join_v1(clear_and_register, create_public_channel)

def test_private_channel(create_private_channel):
    user2 = auth_register_v1("fake1guy@fakeemail.com","fake1password","fake1firstname","fake1lastname") 
    #raising error
    with pytest.raises(AccessError):
        channel_join_v1(user2['auth_user_id'], create_private_channel)

def test_invalid_channel(create_public_channel):
    user2 = auth_register_v1("fake1guy@fakeemail.com","fake1password","fake1firstname","fake1lastname")
    #raising error
    with pytest.raises(InputError):
        channel_join_v1(user2['auth_user_id'], create_public_channel+1)

def test_global_owner_join_private(clear_and_register):
    stream_owner = clear_and_register
    stream_member = auth_register_v1("someguy@fakeemail.com", "fakepassword", "John", "Smith")
    channel1 = channels_create_v1(stream_member['auth_user_id'], 'channel1', False)
    channel_join_v1(stream_owner, channel1['channel_id'])
    channel1_details = channel_details_v1(stream_owner, channel1['channel_id'])
    assert channel1_details['all_members'][0]['u_id'] == stream_owner


