import pytest
import tests.route_helpers as rh
from src.config import url
BASE_URL = url
## =====[ test_channel_ban_v1.py ]===== ##

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
def create_channel(creator_token, invited_members, is_public):
    channel_id = rh.channels_create(creator_token, "chan_name", is_public).json()['channel_id']
    if is_public:
        for member in invited_members:
            rh.channel_join(member, channel_id)
    else:
        for member in invited_members:
            rh.channel_invite(creator_token, channel_id, member)
    return channel_id

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_invalid_channel(clear, user1, user2):
    channel_id = create_channel(user1["token"], [user2["token"]], True)
    kick_response = rh.channel_ban(user1["token"], int(channel_id + 1), user2["auth_user_id"])
    assert kick_response.status_code == 400

def test_invalid_user_ban(clear, user1):
    channel_id = create_channel(user1["token"], [], True)
    kick_response = rh.channel_ban(user1["token"], channel_id, 99999)
    assert kick_response.status_code == 400

def test_self_banning(clear, user1):
    channel_id = create_channel(user1["token"], [], True)
    kick_response = rh.channel_ban(user1["token"], channel_id, user1["auth_user_id"])
    assert kick_response.status_code == 400

def test_owner_ban_owner(clear, user1, user2):
    channel_id = rh.channels_create(user1["token"], "chan_name", True).json()['channel_id']
    rh.channel_join(user2["token"], channel_id)
    rh.channel_addowner(user1["token"], channel_id, user2["auth_user_id"])
    kick_response = rh.channel_ban(user2["token"], channel_id, user1["auth_user_id"])
    assert kick_response.status_code == 400   
    kick_response = rh.channel_ban(user1["token"], channel_id, user2["auth_user_id"])
    assert kick_response.status_code == 400

## Access Error - 403 ##
def test_unauthorised_user(clear, user1, user2, user3):
    channel_id = create_channel(user1["token"], [user2["token"]], True)
    kick_response = rh.channel_ban(user3["token"], channel_id, user2["auth_user_id"])
    assert kick_response.status_code == 403

def test_user_not_owner(clear, user1, user2):
    channel_id = create_channel(user1["token"], [user2["token"]], True)
    kick_response = rh.channel_ban(user2["token"], channel_id, user1["auth_user_id"])
    assert kick_response.status_code == 403

# ==== Tests - Valids ==== #
def test_valid_bans_in_public(clear, user1, user2, user3):
    channel_id = create_channel(user1["token"], [user2["token"], user3["token"]], True)

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
    print(rh.channel_details(user1["token"], channel_id).json())
    assert rh.channel_details(user1["token"], channel_id).json() == expected_output

    ban_response = rh.channel_ban(user1["token"], channel_id, user2["auth_user_id"])
    assert ban_response.status_code == 200

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

    join_response = rh.channel_join(user2["token"], channel_id)
    assert join_response.status_code == 403

    kick_response = rh.channel_ban(user1["token"], channel_id, user3["auth_user_id"])
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

    join_response = rh.channel_join(user3["token"], channel_id)
    assert join_response.status_code == 403

def test_valid_bans_in_private(clear, user1, user2, user3):
    channel_id = create_channel(user1["token"], [user2["auth_user_id"], user3["auth_user_id"]], False)

    expected_output = {
        "name": "chan_name",
        "is_public": False,
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
    print(rh.channel_details(user1["token"], channel_id).json())
    assert rh.channel_details(user1["token"], channel_id).json() == expected_output

    ban_response = rh.channel_ban(user1["token"], channel_id, user2["auth_user_id"])
    assert ban_response.status_code == 200

    expected_output = {
        "name": "chan_name",
        "is_public": False,
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

    join_response = rh.channel_invite(user1["token"], channel_id, user2["auth_user_id"])
    assert join_response.status_code == 400

    kick_response = rh.channel_ban(user1["token"], channel_id, user3["auth_user_id"])
    assert kick_response.status_code == 200

    expected_output = {
        "name": "chan_name",
        "is_public": False,
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

    join_response = rh.channel_invite(user1["token"], channel_id, user3["auth_user_id"])
    assert join_response.status_code == 400
