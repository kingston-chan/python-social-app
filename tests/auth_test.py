import pytest

from src.auth import auth_login_v1, auth_register_v1
from src.error import InputError
from src.other import clear_v1

# auth_register_v1 tests:
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

def test_register_identical_emails():
    clear_v1()
    auth_register_v1("email@email.com", "password", "John", "Smith")

    with pytest.raises(InputError):
        auth_register_v1("email@email.com", "password", "John", "Smith")

#Valid input tests:

def test_register_valid_input():
    clear_v1()
    assert auth_register_v1("email@email.com", "password", "John", "Smith") == {'auth_user_id': 1}

def test_register_valid_numbers():
    clear_v1()
    assert auth_register_v1("161998@439876.com", "2354335425", "24352345", "34553") == {'auth_user_id': 1}

def test_register_symbols_in_name():
    clear_v1()
    assert auth_register_v1("email@email.com", "password", "Jo!@#$%^&*hn", "Smith") == {'auth_user_id': 1}

def test_register_spaces():
    clear_v1()
    assert auth_register_v1("email@email.com", "pass  word", "J o h n ", " S m i t h") == {'auth_user_id': 1}


def test_register_valid_multiple_identical():
    clear_v1()
    assert auth_register_v1("email@email.com", "password", "John", "Smith") == {'auth_user_id': 1}
    assert auth_register_v1("email1@email.com", "password", "John", "Smith") == {'auth_user_id': 2}
    assert auth_register_v1("email2@email.com", "password", "John", "Smith") == {'auth_user_id': 3}


# auth_login_v1 tests:

# Invalid input tests:
def test_login_invalid_email():
    clear_v1()
    auth_register_v1("email@email.com", "password", "John", "Smith") == {'auth_user_id': 1}
    with pytest.raises(InputError):
        auth_login_v1("email", "password")

def test_login_invalid_password():
    clear_v1()
    auth_register_v1("email@email.com", "password", "John", "Smith")
    with pytest.raises(InputError):
        auth_login_v1("email@email.com", "pass")



# Valid input tests:
def test_login_valid_login ():
    clear_v1()
    auth_register_v1("email@email.com", "password", "John", "Smith")
    assert auth_login_v1("email@email.com", "password") == {'auth_user_id': 1}

def test_login_valid_password_in_different_user():
    clear_v1()
    auth_register_v1("email@email.com", "password", "John", "Smith")
    auth_register_v1("email1@email.com", "password", "John", "Smith")
    
    assert auth_login_v1("email1@email.com", "password") == {'auth_user_id': 2}