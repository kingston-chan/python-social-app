import pytest
import tests.route_helpers as rh

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()["token"]

# Valid inputs

# Permission change from member to global owner is successful:

def test_member_to_global(clear_and_register):
    user2 = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()
    user2_token = user2["token"]
    user2_id = user2["user_id"]
    # change user2 to global owner
    rh.admin_userpermission_change(clear_and_register, user2_id, 1)
    # Can join private channels
    channel1_id = rh.channels_create(clear_and_register, "channel1", False).json()["channel_id"]
    rh.channel_join(user2_token, channel1_id)
    user2_channels = rh.channels_list(user2_token).json()["channels"]
    assert user2_channels[0]["channel_id"] == channel1_id
    assert user2_channels[0]["name"] == "channel1"
    # Can remove users
    user3_id = rh.auth_register("random3@gmail.com", "123abc!@#", "Dan", "Smith").json()["auth_user_id"]
    rh.admin_user_remove(user2_token, user3_id)
    assert len(rh.users_all(user2_token).json()["users"]) == 2
    # Can also change others permission
    

# Permission change from global owner to member is successful:
# Cannot join private channels
# Cannot remove users
# Cannot change others permission
# Owner permission in joined channels is revoked

# Invalid inputs

# InputError when any of:
      
# - u_id does not refer to a valid user
# - u_id refers to a user who is the only global owner and they are being demoted to a user
# - permission_id is invalid
      
# AccessError when:

# - the authorised user is not a global owner

# Invalid token

# Invalid session