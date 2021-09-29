import pytest

from src.channel import channel_join_v1
from src.auth import auth_register_v1
from src.auth import auth_login_v1
from src.channels import channels_create_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1

def test_already_member():
    #making user
    clear_v1()
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname") 
    user1 = auth_register_v1("fakeguy1@fakeemail.com","fakepassword1","fakefirstname1","fakelastname1")
    #make a channel
    channel_created = channels_create_v1(user['auth_user_id'], "random_channel_name",True)        
    #intially join channel
    channel_join_v1(user1['auth_user_id'], channel_created['channel_id'])
    #second time join(raising input error)
    with pytest.raises(InputError):
        channel_join_v1(user1['auth_user_id'], channel_created['channel_id'])

def test_private_channel():
    clear_v1()
    #creating users
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname") 
    user1 = auth_register_v1("fake1guy@fakeemail.com","fake1password","fake1firstname","fake1lastname") 
    #creating channels
    channel_created = channels_create_v1(user['auth_user_id'],"random_channel_name","False")
    #raising error
    with pytest.raises(AccessError):
        channel_join_v1(user1['auth_user_id'],channel_created['channel_id'])

def test_invalid_channel():
    clear_v1()
    #making user
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname")
    #making channel
    channel_created = channels_create_v1(user['auth_user_id'],"random_channel_name","True")
    #raising error
    with pytest.raises(AccessError):
        channel_join_v1(user['auth_user_id'],channel_created['channel_id'] + 1)
 
def test_empty_channel_list():
    clear_v1()
    #making user
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname")
    #making channel
    #channel_created = channels_create_v1(user['auth_user_id'],"random_channel_name","True")
    #raising error
    with pytest.raises(AccessError):
        channel_join_v1(user['auth_user_id'], 1)
