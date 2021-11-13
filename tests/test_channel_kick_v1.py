import pytest
import tests.route_helpers as rh

## =====[ test_channel_kick_v1.py ]===== ##

# ==== Fixtures ==== #
@pytest.fixture
def clear():
    rh.clear()

@pytest.fixture
def user1():
    return rh.auth_register("user1@email.com", "password", "user", "one").json()

@pytest.fixture
def user2():
    return rh.auth_register("user2@email.com", "password", "user", "two").json()

@pytest.fixture
def user3():
    return rh.auth_register("user3@email.com", "password", "user", "three").json()

# ==== Helper Functions ==== #
def create_channel(creater_token, invited_members=[]):
    channel_id = rh.channels_create(creater_token, "chan_name", True).json()['channel_id']
    for member in invited_members:
        rh.channel_join(member, channel_id)
    return channel_id

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_invalid_channel(clear, user1, user2):
    channel_id = create_channel(user1["token"], [user2["auth_user_id"]])
    kick_response = rh.channel_kick(user1["token"], channel_id + 1, user2["auth_user_id"]).json()
    assert kick_response.status_code == 400

def test_invalid_user_kicked(clear, user1, user2):
    channel_id = create_channel(user1["token"], [user2["auth_user_id"]])
    kick_response = rh.channel_kick(user1["token"], channel_id, user2["auth_user_id"] + 1).json()
    assert kick_response.status_code == 400

def test_self_kicking(clear, user1):
    channel_id = create_channel(user1["token"])
    kick_response = rh.channel_kick(user1["token"], channel_id, user1["auth_user_id"]).json()
    assert kick_response.status_code == 400

def test_owner_kick_owner(clear, user1, user2):
    channel_id = rh.channels_create(user1["token"], "chan_name", True).json()['channel_id']
    rh.channel_join(user2["auth_user_id"], channel_id)
    rh.channel_addowner(user1["token"], channel_id, user2["auth_user_id"])
    kick_response = rh.channel_kick(user2["token"], channel_id, user1["auth_user_id"]).json()
    assert kick_response.status_code == 400   
    kick_response = rh.channel_kick(user1["token"], channel_id, user2["auth_user_id"]).json()
    assert kick_response.status_code == 400

## Access Error - 403 ##
def test_unauthorised_user(clear, user1, user2, user3):
    channel_id = create_channel(user1["token"], [user2["auth_user_id"]])
    kick_response = rh.channel_kick(user3["token"], channel_id, user2["auth_user_id"]).json()
    assert kick_response.status_code == 400

def test_user_not_owner(clear, user1, user2):
    channel_id = create_channel(user1["token"], [user2["auth_user_id"]])
    kick_response = rh.channel_kick(user2["token"], channel_id, user1["auth_user_id"]).json()
    assert kick_response.status_code == 400

# ==== Tests - Valids ==== #
def test_valid_kicks(clear, user1, user2, user3):
    channel_id = create_channel(user1["token"], [user2["auth_user_id"], user3["auth_user_id"]])

    expected_output = {
        "name": "chan_name",
        "is_public": True,
        "owner_members": [
            {
                'u_id': user1["auth_user_id"],
                'email': 'user1@email.com',
                'name_first': 'user',
                'name_last': 'one',
                'handle_str': 'userone',
                'profile_img_url': f"{url}/imgurl/default.jpg"               
            }
        ],
        "all_members": [
            {
                'u_id': user1["auth_user_id"],
                'email': 'user1@email.com',
                'name_first': 'user',
                'name_last': 'one',
                'handle_str': 'userone',
                'profile_img_url': f"{url}/imgurl/default.jpg"     
            },
            {
                'u_id': user2["auth_user_id"],
                'email': 'user2@email.com',
                'name_first': 'user',
                'name_last': 'two',
                'handle_str': 'usertwo',
                'profile_img_url': f"{url}/imgurl/default.jpg"     
            },
            {
                'u_id': user3["auth_user_id"],
                'email': 'user3@email.com',
                'name_first': 'user',
                'name_last': 'three',
                'handle_str': 'userthree',
                'profile_img_url': f"{url}/imgurl/default.jpg"     
            },
        ]
    }

    assert rh.channel_details(user1["token"], channel_id).json() == expected_output

    kick_response = rh.channel_kick(user1["token"], channel_id, user2["auth_user_id"]).json()
    assert kick_response.status_code == 200

    expected_output = {
        "name": "chan_name",
        "is_public": True,
        "owner_members": [
            {
                'u_id': user1["auth_user_id"],
                'email': 'user1@email.com',
                'name_first': 'user',
                'name_last': 'one',
                'handle_str': 'userone',
                'profile_img_url': f"{url}/imgurl/default.jpg"               
            }
        ],
        "all_members": [
            {
                'u_id': user1["auth_user_id"],
                'email': 'user1@email.com',
                'name_first': 'user',
                'name_last': 'one',
                'handle_str': 'userone',
                'profile_img_url': f"{url}/imgurl/default.jpg"     
            },
            {
                'u_id': user3["auth_user_id"],
                'email': 'user3@email.com',
                'name_first': 'user',
                'name_last': 'three',
                'handle_str': 'userthree',
                'profile_img_url': f"{url}/imgurl/default.jpg"     
            },
        ]
    }

    assert rh.channel_details(user1["token"], channel_id).json() == expected_output

    kick_response = rh.channel_kick(user1["token"], channel_id, user3["auth_user_id"]).json()
    assert kick_response.status_code == 200

    expected_output = {
        "name": "chan_name",
        "is_public": True,
        "owner_members": [
            {
                'u_id': user1["auth_user_id"],
                'email': 'user1@email.com',
                'name_first': 'user',
                'name_last': 'one',
                'handle_str': 'userone',
                'profile_img_url': f"{url}/imgurl/default.jpg"               
            }
        ],
        "all_members": [
            {
                'u_id': user1["auth_user_id"],
                'email': 'user1@email.com',
                'name_first': 'user',
                'name_last': 'one',
                'handle_str': 'userone',
                'profile_img_url': f"{url}/imgurl/default.jpg"     
            },
        ]
    }

    assert rh.channel_details(user1["token"], channel_id).json() == expected_output

