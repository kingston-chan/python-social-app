import pytest
import tests.route_helpers as rh

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()['token']

# ==== Tests with correct input ==== #

# Successfully removes user from channels and DMs
def test_removed_from_channels_dms(clear_and_register):
    user2 = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]
    channel1_id = rh.channels_create(clear_and_register, "channel1", "True").json()["channel_id"]
    rh.channel_join(user2_token, channel1_id)
    dm1_id = rh.dm_create(clear_and_register, [user2_id]).json()["dm_id"]
    rh.admin_user_remove(clear_and_register, user2_id)

    all_users = rh.users_all(clear_and_register).json()["users"]
    assert len(all_users) == 1

    channel1_details = rh.channel_details(clear_and_register, channel1_id).json()
    assert len(channel1_details['all_members']) == 1

    dm1_details = rh.dm_details(clear_and_register, dm1_id).json()
    assert len(dm1_details['members']) == 1

# Removed user's messages are replaced with "Removed user" (channel and dm messages)
def test_removed_users_messages(clear_and_register):
    user2 = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]
    channel1_id = rh.channels_create(clear_and_register, "channel1", "True").json()["channel_id"]
    rh.channel_join(user2_token, channel1_id)
    dm1_id = rh.dm_create(clear_and_register, [user2_id]).json()["dm_id"]
    rh.message_send(user2_token, channel1_id, "hello")
    rh.message_senddm(user2_token, dm1_id, "hello")
    rh.admin_user_remove(clear_and_register, user2_id)

    channel1_messages = rh.channel_messages(clear_and_register, channel1_id, 0).json()["messages"]
    assert channel1_messages[0]["message"] == "Removed user"

    dm1_messages = rh.dm_messages(clear_and_register, dm1_id, 0).json()["messages"]
    assert dm1_messages[0]["message"] == "Removed user"

# Profile is retrieveable but first name is replaced with "Removed" and last name with "user"
def test_removed_users_profile(clear_and_register):
    user2_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    rh.admin_user_remove(clear_and_register, user2_id)
    user2_profile = rh.user_profile(clear_and_register, user2_id)

    assert user2_profile["user"]["name_first"] == "Removed"
    assert user2_profile["user"]["name_last"] == "user"
    assert user2_profile["user"]["email"] is None
    assert user2_profile["user"]["handle_str"] is None

# Removed user's email and handle can be used again
def test_reuseable_email_handle(clear_and_register):
    user2_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    user2_profile = rh.user_profile(clear_and_register, user2_id).json()
    rh.admin_user_remove(clear_and_register, user2_id)
    user3_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    user3_profile = rh.user_profile(clear_and_register, user3_id).json()

    assert user2_profile["email"] == user3_profile["email"]
    assert user2_profile["handle_str"] == user3_profile["handle_str"]


# Global users remove global users (including first owner), given there is more than 1
def test_remove_global_user():
    rh.clear()
    first_owner = rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()
    second_owner = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()
    rh.admin_userpermission_change(first_owner["token"], first_owner["auth_user_id"], 1)
    rh.admin_user_remove(second_owner["token"], first_owner["auth_user_id"])
    first_owner_profile = rh.user_profile(second_owner["token"], first_owner["auth_user_id"]).json()

    assert len(rh.users_all(second_owner["token"]).json()["users"]) == 1
    assert first_owner_profile["user"]["name_first"] == "Removed"
    assert first_owner_profile["user"]["name_last"] == "user"
    

# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    rh.clear()
    response = rh.admin_user_remove("invalidtoken", 1)
    assert response.status_code == 403

# u_id does not refer to valid user (InputError)
def test_invalid_user(clear_and_register):
    response = rh.admin_user_remove(clear_and_register, 99)
    assert response.status_code == 400

# u_id refers to the only Global user (InputError)
def test_remove_only_global_user(clear_and_register):
    response = rh.admin_user_remove(clear_and_register, clear_and_register)
    assert response.status_code == 400

# Authorised user is not a global user(AccessError)
def test_not_authorised_user():
    rh.clear()
    user1_token = rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()["token"]
    user2_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    response = rh.admin_user_remove(user1_token, user2_id)
    assert response.status_code == 403

# Invalid session
# def test_invalid_session(clear_and_register):
#     user2_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
#     rh.auth_logout(clear_and_register)
#     response = rh.admin_user_remove(clear_and_register, user2_id)
#     assert response.status_code == 403

 
