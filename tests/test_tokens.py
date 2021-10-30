import tests.route_helpers as rh

def test_invalid_token_after_clear():
    rh.clear()
    token = rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()['token']

    rh.clear()
    assert rh.channels_create(token, "name", True).status_code == 403

def test_unique_tokens():
    rh.clear()
    token1 = rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()['token']

    rh.clear()
    token2 = rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()['token']

    assert token1 != token2

