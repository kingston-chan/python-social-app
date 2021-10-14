import requests, pytest

BASE_URL = 'http://127.0.0.1:8080'

# ==== Helper functions ==== #

# Registers a user
def register_user(email, password, first_name, last_name):
    user_info = {
        "email": email, 
        "password": password, 
        "name_first": first_name, 
        "name_last": last_name
    }

    return requests.post(f"{BASE_URL}/auth/register/v2", json=user_info).json()

# Creates channel and returns created channel_id
def create_channel(token, name, is_public):
    channel_info = {
        "token": token, 
        "name": name, 
        "is_public": is_public
    }

    return requests.post(f"{BASE_URL}/channels/create/v2", json=channel_info).json()["channel_id"]

# Lists all channels user is in
def list_channels(token):
    return requests.get(f"{BASE_URL}/channels/list/v2", params={ "token": token }).json()

# Lists all existing channels
def list_all_channels(token):
    return requests.get(f"{BASE_URL}/channels/list/v2", params={ "token": token }).json()

# List all DMs user is in
def list_dms(token):
    return requests.get(f"{BASE_URL}/dm/list/v1", params={ "token": token }).json()

# Send a message to DM specified by dm_id
def send_dm(token, dm_id, message):
    return requests.post(f"{BASE_URL}/message/senddm/v1", json={ "token": token, "dm_id": dm_id, "message": message }).json()

# List all messages in DM specified by dm_id
def list_dm_messages(token, dm_id, start):
    return requests.get(f"{BASE_URL}/dm/messages/v1", params={ "token": token, "dm_id": dm_id, "start": start }).json()

# Create a dm with another user(s)
def create_dm(token, u_ids):
    return requests.post(f"{BASE_URL}/dm/create/v1", json={ "token": token, "u_ids": u_ids }).json()

# Send a message in a channel
def send_channel_message(token, channel_id, message):
    return requests.get(f"{BASE_URL}/message/send/v1", params={ "token": token, "channel_id": channel_id, "message": message }).json()

# List all messages in channel
def list_channel_messages(token, channel_id, start):
    return requests.get(f"{BASE_URL}/channel/messages/v2", params={ "token": token, "channel_id": channel_id, "start": start }).json()

# List all users
def list_all_users(token):
    return requests.get(f"{BASE_URL}/users/all/v1", params={ "token": token }).json()

# Return profile of valid user
def user_profile(token, u_id):
    return requests.get(f"{BASE_URL}/user/profile/v1", params={ "token": token, "u_id": u_id }).json()

# Change permission of user
def change_permission(token, u_id, permission_id):
    return requests.post(f"{BASE_URL}/user/profile/v1", json={ "token": token, "u_id": u_id, "permission_id": permission_id })

# Joins a user to a channel
def join_channel(token, channel_id):
    return requests.post(f"{BASE_URL}/user/profile/v1", json={ "token": token, "channel_id": channel_id })

# Removes the user from Streams
def remove_user_global(token, u_id):
    return requests.delete(f"{BASE_URL}/user/profile/v1", json={ "token": token, "u_id": u_id })

# Returns the details of the channel
def show_channel_details(token, channel_id):
    return requests.get(f"{BASE_URL}/channel/details/v2", params={ "token": token, "channel_id": channel_id }).json()

# Returns the details of the DM
def show_dm_details(token, dm_id):
    return requests.get(f"{BASE_URL}/dm/details/v1", params={ "token": token, "dm_id": dm_id }).json()

@pytest.fixture
def clear_and_register():
    requests.delete(f"{BASE_URL}/clear/v1")
    return register_user("random@gmail.com", "123abc!@#", "John", "Smith")['token']

# ==== Tests with correct input ==== #

# Successfully removes user from channels and DMs
def test_removed_from_channels_dms(clear_and_register):
    user2 = register_user("random2@gmail.com", "123abc!@#", "Bob", "Smith")
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]
    channel1_id = create_channel(clear_and_register, "channel1", "True")
    join_channel(user2_token, channel1_id)
    dm1_id = create_dm(clear_and_register, [user2_id])
    remove_user_global(clear_and_register, user2_id)

    all_users = list_all_users(clear_and_register)["users"]
    assert len(all_users) == 1

    channel1_details = show_channel_details(clear_and_register, channel1_id)
    assert len(channel1_details['all_members']) == 1

    dm1_details = show_dm_details(clear_and_register, dm1_id)
    assert len(dm1_details['members']) == 1

# Removed user's messages are replaced with "Removed user" (channel and dm messages)
def test_removed_users_messages(clear_and_register):
    user2 = register_user("random2@gmail.com", "123abc!@#", "Bob", "Smith")
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]
    channel1_id = create_channel(clear_and_register, "channel1", "True")
    join_channel(user2_token, channel1_id)
    dm1_id = create_dm(clear_and_register, [user2_id])
    send_channel_message(user2_token, channel1_id, "hello")
    send_dm(user2_token, dm1_id, "hello")
    remove_user_global(clear_and_register, user2_id)

    channel1_messages = list_channel_messages(clear_and_register, channel1_id, 0)["messages"]
    assert channel1_messages[0]["message"] == "Removed user"

    dm1_messages = list_dm_messages(token, dm1_id, 0)["messages"]
    assert dm1_messages[0]["message"] == "Removed user"

# Profile is retrieveable but first name is replaced with "Removed" and last name with "user"
def test_removed_users_profile(clear_and_register):
    user2 = register_user("random2@gmail.com", "123abc!@#", "Bob", "Smith")
    user2_id = user2["auth_user_id"]
    remove_user_global(clear_and_register, user2_id)
    user2_profile = user_profile(clear_and_register, user2_id)
    assert user2_profile["user"]["name_first"] == "Removed"
    assert user2_profile["user"]["name_last"] == "user"

# Removed user's email and handle can be used
def test_reuseable_email_handle(clear_and_register):
    user2_id = register_user("random2@gmail.com", "123abc!@#", "Bob", "Smith")["auth_user_id"]
    user2_profile = user_profile(clear_and_register, user2_id)
    remove_user_global(clear_and_register, user2_id)
    user3_id = register_user("random2@gmail.com", "123abc!@#", "Bob", "Smith")["auth_user_id"]
    user3_profile = user_profile(clear_and_register, user3_id)

    assert user2_profile["email"] == user3_profile["email"]
    assert user2_profile["handle_str"] == user3_profile["handle_str"]


# Global users remove global users (including first owner), given there is more than 1
def test_remove_global_user():
    requests.delete(f"{BASE_URL}/clear/v1")
    first_owner = register_user("random@gmail.com", "123abc!@#", "John", "Smith")
    second_owner = register_user("random2@gmail.com", "123abc!@#", "Bob", "Smith")
    change_permission(first_owner["token"], first_owner["auth_user_id"], 1)
    remove_user_global(second_owner["token"], first_owner["auth_user_id"])
    first_owner_profile = user_profile(second_owner["token"], first_owner["auth_user_id"])

    assert len(list_all_users(second_owner["token"])["users"]) == 1
    assert first_owner_profile["user"]["name_first"] == "Removed"
    assert first_owner_profile["user"]["name_last"] == "user"
    

# ==== Tests with incorrect/invalid input ==== #

# Invalid token

# u_id does not refer to valid user (InputError)

# u_id refers to the only Global user (InputError)

# Authorised user is not a global user(AccessError)




 
