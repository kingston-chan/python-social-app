import pytest
from src.config import url
import tests.route_helpers as rh

BASE_URL = url

@pytest.fixture
def clear():
    return rh.clear()

@pytest.fixture
def first_user_data():
    response = rh.auth_register("keefe@gmail.com", "password", "keefe", "vuong")
    return response.json()

@pytest.fixture
def second_user_data():
    response = rh.auth_register("eagle@gmail.com", "password", "team", "eagle")
    return response.json()  

@pytest.fixture
def third_user_data():
    response = rh.auth_register("butcher@gmail.com", "password", "knife", "butcher")
    return response.json()

def test_dm_leave_multiple_dms_valid(clear, first_user_data, second_user_data):

    response = rh.dm_create(first_user_data["token"], [second_user_data["auth_user_id"]])
    response_data = response.json()
    dm_id = response_data["dm_id"]

    response = rh.dm_create(second_user_data["token"], [first_user_data["auth_user_id"]])

    response = rh.dm_leave(second_user_data["token"], dm_id)

    response = rh.dm_details(first_user_data["token"], dm_id)
    response_data = response.json()

    expected_output = {
        "name": "keefevuong, teameagle",
        "members": [
            {
                'u_id': first_user_data["auth_user_id"],
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',
                'profile_img_url': f"{url}/imgurl/default.jpg"    
            }
        ]
    }

    assert response_data == expected_output

def test_dm_leave_invalid_dm_id(clear, first_user_data, second_user_data):

    response = rh.dm_create(first_user_data["token"], [second_user_data["auth_user_id"]])

    fake_dm_id = 9999

    response = rh.dm_leave(second_user_data["token"], fake_dm_id)

    assert response.status_code == 400

def test_dm_leave_not_a_member_of_dm(clear, first_user_data, second_user_data, third_user_data):

    response = rh.dm_create(first_user_data["token"], [second_user_data["auth_user_id"]])
    response_data = response.json()
    dm_id = response_data["dm_id"]

    response = rh.dm_leave(third_user_data["token"], dm_id)

    assert response.status_code == 403

def test_dm_leave_unauthorised_token(clear, first_user_data, second_user_data):

    response = rh.dm_create(first_user_data["token"], [second_user_data["auth_user_id"]])
    response_data = response.json()
    dm_id = response_data["dm_id"]
    
    fake_token = "asfoipjasoifj"

    response = rh.dm_leave(fake_token, dm_id)

    assert response.status_code == 403

def test_dm_leave_valid(clear, first_user_data, second_user_data):

    response = rh.dm_create(first_user_data["token"], [second_user_data["auth_user_id"]])
    response_data = response.json()
    dm_id = response_data["dm_id"]

    response = rh.dm_leave(second_user_data["token"], dm_id)

    response = rh.dm_details(first_user_data["token"], dm_id)
    response_data = response.json()

    expected_output = {
        "name": "keefevuong, teameagle",
        "members": [
            {
                'u_id': first_user_data["auth_user_id"],
                'email': 'keefe@gmail.com',
                'name_first': 'keefe',
                'name_last': 'vuong',
                'handle_str': 'keefevuong',
                'profile_img_url': f"{url}/imgurl/default.jpg"     
            }
        ]
    }

    assert response_data == expected_output

def test_dm_leave_owner_leaves_dm(clear, first_user_data, second_user_data):

    response = rh.dm_create(first_user_data["token"], [second_user_data["auth_user_id"]])
    response_data = response.json()
    dm_id = response_data["dm_id"]

    response = rh.dm_leave(first_user_data["token"], dm_id) 

    response = rh.dm_details(second_user_data["token"], dm_id)
    response_data = response.json()

    expected_output = {
        "name": "keefevuong, teameagle",
        "members": [
            {
                'u_id': second_user_data["auth_user_id"],
                'email': 'eagle@gmail.com',
                'name_first': 'team',
                'name_last': 'eagle',
                'handle_str': 'teameagle',
                'profile_img_url': f"{url}/imgurl/default.jpg"     
            }
        ]
    }

    assert response_data == expected_output