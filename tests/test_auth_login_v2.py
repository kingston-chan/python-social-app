import pytest, jwt, secrets
import tests.route_helpers as rh
from src import config

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("email@email.com", "password", "Julian", "Winzer")

# Invalid input tests:

def test_login_invalid_email(clear_and_register):
    response = rh.auth_login("email", "password")
    assert response.status_code == 400

def test_login_invalid_password(clear_and_register):
    response = rh.auth_login("email@email.com", "pass")
    assert response.status_code == 400


# Valid input tests:

def test_login_to_correct_user(clear_and_register):
    tok = clear_and_register.json()["token"]
    channel1_id = rh.channels_create(tok, "channel1", True).json()["channel_id"]
    tok1 = rh.auth_login("email@email.com", "password").json()["token"]
    # Channels_list lists all channels that user of token is a member of, 
    # therefore the only channel the login token is a member of is channel1
    channel1 = rh.channels_list(tok1).json()["channels"][0]
    channel1["name"] == "channel1"
    channel1["channel_id"] == channel1_id
    

def test_multiple_logins_possible(clear_and_register):
    assert rh.auth_login("email@email.com", "password").status_code == 200
    assert rh.auth_login("email@email.com", "password").status_code == 200
    assert rh.auth_login("email@email.com", "password").status_code == 200
    assert rh.auth_login("email@email.com", "password").status_code == 200
    assert rh.auth_login("email@email.com", "password").status_code == 200
    assert rh.auth_login("email@email.com", "password").status_code == 200

# Test token validity 

def test_login_valid_input():
    rh.clear()
    rh.auth_register("email@email.com", "password", "Julian", "Winzer")

    response = rh.auth_login("email@email.com", "password")
    response_data = response.json()

    assert response_data["auth_user_id"] == 1

    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])

    assert token["user_id"] == 1
    assert token["session_id"] == 2

def test_login_valid_multiple_times():
    rh.clear()
    rh.auth_register("email@email.com", "password", "Julian", "Winzer")

    rh.auth_login("email@email.com", "password")
    response = rh.auth_login("email@email.com", "password")
    response_data = response.json()

    assert response_data["auth_user_id"] == 1

    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])
    
    assert token["user_id"] == 1
    assert token["session_id"] == 3

def test_login_valid_multiple_users():
    rh.clear()
    rh.auth_register("email@email.com", "password", "Julian", "Winzer")
    rh.auth_register("email2@email.com", "password", "Julian", "Winzer")
    rh.auth_register("email3@email.com", "password", "Julian", "Winzer")

    response = rh.auth_login("email3@email.com", "password")
    response_data = response.json()

    assert response_data["auth_user_id"] == 3

    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])
    assert token["user_id"] == 3
    assert token["session_id"] == 4
