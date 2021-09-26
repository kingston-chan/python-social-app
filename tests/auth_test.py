import pytest

from src.auth import auth_register_v1
from src.error import InputError

def test_register_invalid_email():
    with pytest.raises(InputError):
        auth_register_v1("email", "password", "John", "Smith")

def test_register_invalid_password():
    with pytest.raises(InputError):
        auth_register_v1("email@email.com", "pa", "John", "Smith")


def test_register_invalid_fName():
    with pytest.raises(InputError):
        auth_register_v1("email@email.com", "pass", "", "Smith")

def test_register_invalid_lName():
    with pytest.raises(InputError):
        auth_register_v1("email@email.com", "pass", "John", "")

def test_valid_input():
    assert auth_register_v1("email@email.com", "pass", "John", "Smith") == 1
