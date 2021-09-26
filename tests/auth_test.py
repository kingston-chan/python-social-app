import pytest

from src.auth import auth_register_v1
from src.error import InputError

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

#Valid input test
def test_valid_input():
    assert auth_register_v1("email@email.com", "pass", "John", "Smith") == 1
