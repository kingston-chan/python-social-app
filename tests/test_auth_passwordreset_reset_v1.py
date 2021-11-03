import tests.route_helpers as rh
import pytest
# Can only test two things, the input errors

@pytest.fixture
def clear_and_register():
    rh.clear()
    rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith")
    rh.auth_passwordreset_request("random@gmail.com")

def test_invalid_reset_code(clear_and_register):
    assert rh.auth_passwordreset_reset("invalidresetcode", "validpassword").status_code == 400


def test_invalid_password(clear_and_register):
    assert rh.auth_passwordreset_reset("resetcode", "pass").status_code == 400