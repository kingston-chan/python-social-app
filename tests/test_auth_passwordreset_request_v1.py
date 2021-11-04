import tests.route_helpers as rh
import pytest

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()["token"]

def test_invalid_and_valid_email(clear_and_register):
    assert rh.auth_passwordreset_request("random@gmail.com").status_code == 200
    assert rh.auth_passwordreset_request("bademail@gmail.com").status_code == 200
    assert rh.auth_passwordreset_request("bademail").status_code == 200

# If a valid email is given, it will log out any ongoing sessions corresponding to that
# email.
def test_passwordreset_request_logs_out_all_sessions(clear_and_register):
    rh.auth_passwordreset_request("random@gmail.com")
    assert rh.channels_create(clear_and_register, "channel", True).status_code == 403

# Working email
def test_works():
    rh.clear()
    rh.auth_register("h13beaglestreamsuser@gmail.com", "123abc!@#", "John", "Smith").json()["token"]
    assert rh.auth_passwordreset_request("h13beaglestreamsuser@gmail.com").status_code == 200
