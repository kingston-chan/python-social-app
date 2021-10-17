import pytest
from src import channel
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
    user2_id = user2["auth_user_id"]
    channel1_id = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    rh.channel_join(user2_token, channel1_id)
    # change user2 to global owner
    rh.admin_userpermission_change(clear_and_register, user2_id, 1)

    # Can join private channels
    channel2_id = rh.channels_create(clear_and_register, "channel2", False).json()["channel_id"]
    rh.channel_join(user2_token, channel2_id)
    user2_channels = rh.channels_list(user2_token).json()["channels"]
    assert user2_channels[1]["channel_id"] == channel2_id
    assert user2_channels[1]["name"] == "channel2"

    # # Can remove users
    # user3_id = rh.auth_register("random3@gmail.com", "123abc!@#", "Dan", "Smith").json()["auth_user_id"]
    # rh.admin_user_remove(user2_token, user3_id)
    # assert len(rh.users_all(user2_token).json()["users"]) == 2

    # Can also change others permission
    user1_id = rh.auth_login("random@gmail.com", "123abc!@#").json()["auth_user_id"]
    response = rh.admin_userpermission_change(user2_token, user1_id, 2)
    assert response.status_code == 200

    # Has channel owner permissions, can remove and add owner
    user3 = rh.auth_register("random3@gmail.com", "123abc!@#", "Dan", "Smith").json()
    user3_id = user3["auth_user_id"]
    user3_token = user3["token"]
    rh.channel_invite(user2_token, channel2_id, user3_id)
    rh.channel_addowner(user2_token, channel2_id, user3_id)
    channel2_details = rh.channel_details(user2_token, channel2_id).json()
    
    assert len(channel2_details["owner_members"]) == 2
    assert user3_id == channel2_details["owner_members"][1]["u_id"]

    rh.channel_removeowner(user2_token, channel2_id, user3_id)
    channel2_details = rh.channel_details(user2_token, channel2_id).json()
    assert len(channel2_details["owner_members"]) == 1

    # Gains owner permissions for channels previously joined (before permissions change)
    rh.channel_join(user3_token, channel1_id)
    rh.channel_addowner(user2_token, channel1_id, user3_id)
    channel1_details = rh.channel_details(user2_token, channel1_id).json()

    assert len(channel1_details["owner_members"]) == 2
    assert user3_id == channel1_details["owner_members"][1]["u_id"]

    rh.channel_removeowner(user2_token, channel1_id, user3_id)
    channel1_details = rh.channel_details(user2_token, channel1_id).json()
    assert len(channel1_details["owner_members"]) == 1

# # Permission change from global owner to member is successful:
def test_global_to_member(clear_and_register):
    user2 = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]
    channel1_id = rh.channels_create(user2_token, "channel1", True).json()["channel_id"]
    rh.channel_join(clear_and_register, channel1_id)

    # change user2 to global owner
    rh.admin_userpermission_change(clear_and_register, user2_id, 1)
    user1_id = rh.auth_login("random@gmail.com", "123abc!@#").json()["auth_user_id"]

    # change user1 to member
    rh.admin_userpermission_change(user2_token, user1_id, 2)

    # Cannot join private channels
    channel2_id = rh.channels_create(user2_token, "channel2", False).json()["channel_id"]
    response = rh.channel_join(clear_and_register, channel2_id)
    assert response.status_code == 403

#     # Cannot remove users
#     response = rh.admin_user_remove(clear_and_register, user3_id)
#     assert response.status_code == 403

    # Cannot change others permission
    user3_id = rh.auth_register("random3@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    response = rh.admin_userpermission_change(clear_and_register, user3_id, 1)
    assert response.status_code == 403

    # Owner permission in joined channels is revoked
    response = rh.channel_addowner(clear_and_register, channel1_id, user3_id)
    assert response.status_code == 403

# Invalid inputs

# InputError when any of:
      
# - u_id does not refer to a valid user
def test_invalid_uid(clear_and_register):
    response = rh.admin_userpermission_change(clear_and_register, 99, 1)
    assert response.status_code == 400

# - u_id refers to a user who is the only global owner and they are being demoted to a user
# def test_only_global_onwer_demoted(clear_and_register):
#     global_owner_id = rh.auth_login("random@gmail.com", "123abc!@#").json()["auth_user_id"]
#     response = rh.admin_userpermission_change(clear_and_register, global_owner_id, 2)
#     assert response.status_code == 400

# - permission_id is invalid
def test_invalid_permission_id(clear_and_register):
    user2_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    response = rh.admin_userpermission_change(clear_and_register, user2_id, 3)
    assert response.status_code == 400
      
# AccessError when:

# - the authorised user is not a global owner
def test_auth_user_not_global_owner():
    rh.clear()
    rh.auth_register("random1@gmail.com", "123abc!@#", "Dan", "Smith")
    user2_token = rh.auth_register("random2@gmail.com", "123abc!@#", "John", "Smith").json()["token"]
    user3_id = rh.auth_register("random3@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    response = rh.admin_userpermission_change(user2_token, user3_id, 1)
    assert response.status_code == 403

# Invalid token
def test_invalid_token():
    rh.clear()
    user2_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    response = rh.admin_userpermission_change("invalidtoken", user2_id, 1)
    assert response.status_code == 403

# Invalid session
# def test_invalid_session(clear_and_register):
#     user2_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
#     rh.auth_logout(clear_and_register)
#     response = rh.admin_userpermission_change(clear_and_register, user2_id, 1)
#     assert response.status_code == 403
