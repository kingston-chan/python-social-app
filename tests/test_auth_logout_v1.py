import pytest
import tests.route_helpers as rh

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("email@email.com", "password", "Julian", "Winzer").json()["token"]

def test_logout(clear_and_register):
    token = rh.auth_login("email@email.com", "password").json()["token"]
    assert rh.auth_logout(token).status_code == 200

def test_logout_invalidates_token(clear_and_register):
    rh.auth_logout(clear_and_register)
    assert rh.channels_create(clear_and_register, "name", True).status_code == 403
    assert rh.dm_create(clear_and_register, []).status_code == 403
    assert rh.user_profile_sethandle(clear_and_register, "newhandle").status_code == 403
    assert rh.user_profile_setname(clear_and_register, "new", "name").status_code == 403
    assert rh.user_profile_setemail(clear_and_register, "newemail@email.com").status_code == 403

def test_invalid_token():
    rh.clear()
    assert rh.auth_logout("invalid_token").status_code == 403
    


