import pytest

from src.channel import channel_invite_v1
from src.auth import auth_register_v1
from src.auth import auth_login_v1
from src.channels import channels_create_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1       

@pytest.fixture 
def creating_user():
    user = auth_register_v1("fakeguy@fakeemail.com","fakepassword","fakefirstname","fakelastname") 
    return user['auth_user_id']    
    
@pytest.fixture
def creating_channel(creating_user):
    channel_created = channels_create_v1(creating_user, "random_channel_name",True)
    return channel_created['channel_id']  
      
def test_already_member():
    clear_v1()
    #raising error    
    with pytest.raises(InputError):
        channel_invite_v1(creating_user, creating_channel,creating_user)
        
def test_not_valid_user():
    clear_v1()
    #raising error
    with pytest.raises(InputError):
        channel_invite_v1(creating_user, creating_channel, 9999999999999999999999999999999999999)

def test_not_valid_channel():
    clear_v1()
    #making user
    user1 = auth_register_v1("fakeguy1@fakeemail.com","fakepassword1","fakefirstname1","fakelastname1") 
    #raising error
    with pytest.raises(InputError):
        channel_invite_v1(creating_user, 9999999999999999999999999999, user1['auth_user_id'])

def test_authuser_not_valid():
    clear_v1()
    #making user
    user1 = auth_register_v1("fakeguy1@fakeemail.com","fakepassword1","fakefirstname1","fakelastname1") 
    #raising error
    with pytest.raises(AccessError):
        channel_invite_v1(user1['auth_user_id'], creating_channel, user1['auth_user_id'])
        
 
    
    
    
    
    
    
    
    

    

