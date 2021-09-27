import pytest

from src.auth import auth_register_v1
from src.error import InputError
from src.other import clear_v1

#Invalid input tests:

#Test for InputError when email, password, first name or last name are invalid
def test_register_invalid_email():
    with pytest.raises(InputError):
        auth_register_v1("email", "password", "John", "Smith")

def test_register_invalid_password():
    with pytest.raises(InputError):
        auth_register_v1("email@email.com", "pass", "John", "Smith")


def test_register_invalid_fName():
    with pytest.raises(InputError):
        auth_register_v1("email@email.com", "pass", "", "Smith")

def test_register_invalid_lName():
    with pytest.raises(InputError):
        auth_register_v1("email@email.com", "pass", "John", "")

def test_register_invalid_multiple():
    with pytest.raises(InputError):
        auth_register_v1("email", "pass", "John", "")

#Valid input tests:

def test_valid_input():
    clear_v1()
    assert auth_register_v1("email@email.com", "password", "John", "Smith") == {'auth_user_id': 1}

def test_valid_numbers():
    clear_v1()
    assert auth_register_v1("161998@439876.com", "2354335425", "24352345", "34553") == {'auth_user_id': 1}

def test_symbols_in_name():
    clear_v1()
    assert auth_register_v1("email@email.com", "password", "Jo!@#$%^&*hn", "Smith") == {'auth_user_id': 1}

def test_spaces():
    clear_v1()
    assert auth_register_v1("email@email.com", "pass  word", "J o h n ", " S m i t h") == {'auth_user_id': 1}


def test_valid_multiple_identical():
    clear_v1()
    assert auth_register_v1("email@email.com", "password", "John", "Smith") == {'auth_user_id': 1}
    assert auth_register_v1("email@email.com", "password", "John", "Smith") == {'auth_user_id': 2}
    assert auth_register_v1("email@email.com", "password", "John", "Smith") == {'auth_user_id': 3}