import pytest

from src.channel import channel_invite_v1
from src.auth import auth_register_v1
from src.auth import auth_login_v1
from src.channels import channels_create_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1

def pytest.fixture():  ---- return auth id
                            return channel_id



def test_already_member():
    clear_v1()
    #making user
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname") 
    #make a channel
    channel_created = channels_create_v1(user['auth_user_id'], "random_channel_name",True)
    #raising error
    with pytest.raises(InputError):
        channel_invite_v1(user['auth_user_id'], channel_created['channel_id'],user['auth_user_id'])
        
def test_not_valid_user():
    clear_v1()
    #making user
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname") 
    #make a channel
    channel_created = channels_create_v1(user['auth_user_id'], "random_channel_name",True)
    #raising error
    with pytest.raises(InputError):
        channel_invite_v1(user['auth_user_id'], channel_created['channel_id'], user['auth_user_id'] + 1)

def test_not_valid_channel():
    clear_v1()
    #making user
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname") 
    user1 = auth_register_v1("fakeguy1@fakeemail.com","fakepassword1","fakefirstname1","fakelastname1") 
    #make a channel
    channel_created = channels_create_v1(user['auth_user_id'], "random_channel_name",True)
    #raising error
    with pytest.raises(InputError):
        channel_invite_v1(user['auth_user_id'], channel_created['channel_id'] + 1, user1['auth_user_id'])

def test_authuser_not_valid():
    clear_v1()
    #making user
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname") 
    user1 = auth_register_v1("fakeguy1@fakeemail.com","fakepassword1","fakefirstname1","fakelastname1") 
    #make a channel
    channel_created = channels_create_v1(user['auth_user_id'], "random_channel_name",True)
    #raising error
    with pytest.raises(AccessError):
        channel_invite_v1(user1['auth_user_id'], channel_created['channel_id'], user1['auth_user_id'])
        
 
    
    
    
    
    
    
    
    

    

