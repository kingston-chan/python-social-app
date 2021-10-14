import requests

BASE_URL = 'http://127.0.0.1:6969'

# Invalid input tests:

def test_register_invalid_email():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)

    assert response.status_code == 400


def test_register_invalid_password():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "pass",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)

    assert response.status_code == 400


def test_register_invalid_fName():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "",
        "name_last": "Winzer"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)

    assert response.status_code == 400


def test_register_invalid_lName():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": ""
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)

    assert response.status_code == 400


def test_register_invalid_multiple():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "pass",
        "name_first": "Julian",
        "name_last": ""
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)

    assert response.status_code == 400

def test_register_identical_emails():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)

    assert response.status_code == 400

# Valid input tests:

def test_register_valid_input():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    #assert response_data["users"][0]["token"] == token

def test_register_valid_numbers():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "161998@439876.com",
        "password": "2354335425",
        "name_first": "24352345",
        "name_last": "34553"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    #assert response_data["users"][0]["token"] == token

def test_register_valid_symbols():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Ju!@#$%^&*lian",
        "name_last": "Winzer"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    #assert response_data["users"][0]["token"] == token

def test_register_valid_spaces():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": " J u l i a n ",
        "name_last": " W i n z e r "
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()

    assert response_data["auth_user_id"] == 1
    #assert response_data["users"][0]["token"] == token

def test_register_valid_multiple_identical():
    requests.delete(f"{BASE_URL}/clear/v1")

    user_data = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data)
    response_data = response.json()

    assert response_data["auth_user_id"] == 1

    user_data2 = {
        "email": "email@email.com",
        "password": "password",
        "name_first": "Julian",
        "name_last": "Winzer"
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json=user_data2)
    response_data = response.json()

    assert response_data["auth_user_id"] == 2


    #assert response_data["users"][0]["token"] == token