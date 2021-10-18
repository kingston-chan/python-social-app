import pytest
import tests.route_helpers as rh

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()["token"]

# ==== Tests with correct input ==== #

# Lists all users given valid token
def test_list_all_users(clear_and_register):

    user1_id = rh.auth_login("random@gmail.com", "123abc!@#").json()["auth_user_id"]
    user2_id = rh.auth_register("random1@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    user3_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Dan", "Smith").json()["auth_user_id"]

    response = rh.users_all(clear_and_register)
    assert response.status_code == 200

    all_users = response.json()["users"]

    assert len(all_users) == 3

    assert all_users[0]["u_id"] == user1_id
    assert all_users[1]["u_id"] == user2_id
    assert all_users[2]["u_id"] == user3_id

    assert all_users[0]["email"] == "random@gmail.com"
    assert all_users[1]["email"] == "random1@gmail.com"
    assert all_users[2]["email"] == "random2@gmail.com"

    assert all_users[0]["name_first"] == "John"
    assert all_users[1]["name_first"] == "Bob"
    assert all_users[2]["name_first"] == "Dan"

# Lists all valid users, i.e. not removed
def test_list_valid_users(clear_and_register):
    user1_id = rh.auth_login("random@gmail.com", "123abc!@#").json()["auth_user_id"]
    user2_id = rh.auth_register("random1@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    user3_id = rh.auth_register("random2@gmail.com", "123abc!@#", "Danny", "Smith").json()["auth_user_id"]

    rh.admin_user_remove(clear_and_register, user2_id)

    all_users = rh.users_all(clear_and_register).json()["users"]

    assert len(all_users) == 2

    assert all_users[0]["u_id"] == user1_id
    assert all_users[1]["u_id"] == user3_id

    assert all_users[0]["email"] == "random@gmail.com"
    assert all_users[1]["email"] == "random2@gmail.com"

    assert all_users[0]["name_first"] == "John"
    assert all_users[1]["name_first"] == "Danny"


# ==== Tests with incorrect/invalid input ==== #

# Invalid token
def test_invalid_token():
    rh.clear()
    response = rh.users_all("invalidtoken")
    assert response.status_code == 403

# Invalid session
def test_invalid_session(clear_and_register):
    rh.auth_logout(clear_and_register)
    response = rh.users_all(clear_and_register)
    assert response.status_code == 403
