import route_helpers as rh

def test_invalid_and_valid_email():
    rh.clear()
    rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith")

    assert rh.auth_passwordreset_request("random@gmail.com").status_code == 200
    assert rh.auth_passwordreset_request("bademail@gmail.com").status_code == 200
    assert rh.auth_passwordreset_request("bademail").status_code == 200

# If a valid email is given, it will log out any ongoing sessions corresponding to that
# email.
def test_passwordreset_request_logs_out_all_sessions():
    rh.clear()
    token = rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()["token"]

    rh.auth_passwordreset_request("random@gmail.com")

    assert rh.channels_create(token, "channel", True).status_code == 403
    