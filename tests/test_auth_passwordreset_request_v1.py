import route_helpers as rh

def test_invalid_and_valid_email():
    rh.clear()
    rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith")

    assert rh.auth_passwordreset_request("random@gmail.com").status_code == 200
    assert rh.auth_passwordreset_request("bademail@gmail.com").status_code == 200
    assert rh.auth_passwordreset_request("bademail").status_code == 200
