import jwt
import tests.route_helpers as rh
from src import config


# Invalid input tests:

def test_register_invalid_email():
    rh.clear()
    response = rh.auth_register("email", "password", "Julian", "Winzer")
    assert response.status_code == 400


def test_register_invalid_password():
    rh.clear()
    response = rh.auth_register("email@email.com", "pass", "Julian", "Winzer")
    assert response.status_code == 400

def test_register_invalid_fName():
    rh.clear()
    response = rh.auth_register("email@email.com", "password", "", "Winzer")
    assert response.status_code == 400

def test_register_invalid_lName():
    rh.clear()
    response = rh.auth_register("email@email.com", "password", "Julian", "")
    assert response.status_code == 400


def test_register_invalid_multiple():
    rh.clear()
    response = rh.auth_register("email@email.com", "pass", "Julian", "")
    assert response.status_code == 400

def test_register_identical_emails():
    rh.clear()
    rh.auth_register("email@email.com", "password", "Julian", "Winzer")
    response = rh.auth_register("email@email.com", "password", "Julian", "Winzer")
    assert response.status_code == 400

# Valid input tests:

def test_successful_register():
    rh.clear()
    user = rh.auth_register("email@email.com", "password", "Julian", "Winzer").json()
    user_tok = user["token"]
    user_id = user["auth_user_id"]

    user_profile = rh.user_profile(user_tok, user_id).json()["user"]

    assert user_profile["u_id"] == user_id
    assert user_profile["email"] == "email@email.com"
    assert user_profile["name_first"] == "Julian"
    assert user_profile["name_last"] == "Winzer"
    assert user_profile["handle_str"] == "julianwinzer"

def test_register_valid_input():
    rh.clear()
    response = rh.auth_register("email@email.com", "password", "Julian", "Winzer")
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])
    assert token["user_id"] == 1
    assert token["session_id"] == 1


def test_register_valid_numbers():
    rh.clear()
    response = rh.auth_register("161998@439876.com", "2354335425", "24352345", "34553")
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])
    assert token["user_id"] == 1
    assert token["session_id"] == 1

def test_register_valid_symbols():
    rh.clear()
    response = rh.auth_register("email@email.com", "password", "Ju!@#$%^&*lian", "Winzer")
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])
    assert token["user_id"] == 1
    assert token["session_id"] == 1

def test_register_valid_spaces():
    rh.clear()
    response = rh.auth_register("email@email.com", "password", " J u l i a n ", " W i n z e r ")
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])
    assert token["user_id"] == 1
    assert token["session_id"] == 1

def test_register_valid_multiple_identical():
    rh.clear()
    response = rh.auth_register("email@email.com", "password", "Julian", "Winzer")
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])
    assert token["user_id"] == 1
    assert token["session_id"] == 1

    response = rh.auth_register("email2@email.com", "password", "Julian", "Winzer")
    response_data = response.json()

    assert response_data["auth_user_id"] == 2
    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])
    assert token["user_id"] == 2
    assert token["session_id"] == 2

def test_register_valid_long_handle():
    rh.clear()
    response = rh.auth_register("email2@email.com", "password", "ThisHandleIsTooLong", "ThisHandleIsTooLong")
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    token = jwt.decode(response_data["token"], config.hashcode, algorithms=['HS256'])
    assert token["user_id"] == 1
    assert token["session_id"] == 1