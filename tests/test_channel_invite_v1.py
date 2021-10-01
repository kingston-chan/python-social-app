import pytest

from src.channel import channel_invite_v1
from src.auth import auth_register_v1
from src.auth import auth_login_v1
from src.channels import channels_create_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1       

@pytest.fixture
def create_user():
    clear_v1()
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname")
    auth_user_id = user['auth_user_id']
    return auth_user_id  
    
@pytest.fixture
def create_channel(create_user):
    channel_created = channels_create_v1(create_user, "random_channel_name",True)
    return channel_created['channel_id']
    
def test_already_member(create_user , create_channel):
    with pytest.raises(InputError):
        channel_invite_v1(create_user, create_channel,create_user)
        
def test_not_valid_user(create_user , create_channel):
    #raising error
    with pytest.raises(InputError):
        channel_invite_v1(create_user, create_channel, -1)

def test_not_valid_channel(create_user , create_channel):
    #making user
    user1 = auth_register_v1("fakeguy1@fakeemail.com","fakepassword1","fakefirstname1","fakelastname1") 
    #raising error
    with pytest.raises(InputError):
        channel_invite_v1(create_user, -1, user1['auth_user_id'])

def test_authuser_not_valid(create_channel):
    #making user
    user1 = auth_register_v1("fakeguy1@fakeemail.com","fakepassword1","fakefirstname1","fakelastname1") 
    #raising error
    with pytest.raises(AccessError):
        channel_invite_v1(user1['auth_user_id'], create_channel, user1['auth_user_id'])
 
    
    
    
    
    
    
    
    

    

