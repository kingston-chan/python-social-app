import pytest
from src.config import url
import json
import tests.route_helpers as rh
import requests

BASE_URL = url
SAMPLE_JPEG_IMG_LINK = "http://adaptive-images.com/content/images/winter.jpg"
SAMPLE_JPEG_IMG_LINK2 = "http://adaptive-images.com/content/images/sunset.jpg"
SAMPLE_PNG_IMG_LINK = "http://www.libjpg.org/pub/jpg/img_jpg/jpglogo--povray-3.7--black826--800x600.png"
SAMPLE_HTTPS_JPEG_LINK = "https://res.cloudinary.com/demo/image/upload/q_90/happy_dog.jpg"
## =====[ test_user_profile_uploadphoto_v1.py ]===== ##

# ==== Fixtures ==== #
@pytest.fixture
def clear():
    rh.clear()

@pytest.fixture
def user1():
    return rh.auth_register("user1@email.com", "password", "user", "name").json()

@pytest.fixture
def user2():
    return rh.auth_register("user2@email.com", "password", "user", "name").json()

@pytest.fixture
def user3():
    return rh.auth_register("user3@email.com", "password", "user", "name").json()

# ==== Tests - Errors ==== #
## Input Error - 400 ##
def test_img_url_fake_website(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], "http://www.fdsagas2134134fbsafbs.com/img", 0, 0, 700, 700)
    assert response.status_code == 400

def test_img_url_https(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_HTTPS_JPEG_LINK, 0, 0, 700, 700)
    assert response.status_code == 400

def test_img_url_fake_website_img(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], "http://www.fdsagas2134134fbsafbs.com/fakeimg.jpg", 0, 0, 700, 700)
    assert response.status_code == 400

def test_invalid_x_start(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK, -1, 0, 700, 700)
    assert response.status_code == 400

def test_invalid_y_start(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK, 0, -1, 700, 700)
    assert response.status_code == 400

def test_invalid_x_end(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK, 0, 0, -1, 700)
    assert response.status_code == 400

def test_invalid_y_end(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK, 0, 0, 700, -1)
    assert response.status_code == 400

def test_x_end_less_than_x_start(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK, 700, 0, 600, 700)
    assert response.status_code == 400

def test_y_end_less_than_y_start(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK, 0, 700, 700, 600)
    assert response.status_code == 400

def test_image_not_jpeg(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_PNG_IMG_LINK, 0, 0, 700, 700)
    assert response.status_code == 400


# ==== Tests - Valids ==== #
def test_default_photo(clear, user1):
    response = requests.get(f"{url}/imgurl/default.jpg")
    assert response.status_code == 200

def test_valid_photo(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK, 0, 0, 700, 700)
    assert response.status_code == 200
    user1_prof = rh.user_profile(user1["token"], user1["auth_user_id"]).json()["user"]
    response = requests.get(user1_prof["profile_img_url"])
    assert response.status_code == 200

def test_valid_photos(clear, user1):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK, 0, 0, 700, 700)
    assert response.status_code == 200
    user1_prof = rh.user_profile(user1["token"], user1["auth_user_id"]).json()["user"]
    response = requests.get(user1_prof["profile_img_url"])
    assert response.status_code == 200

    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK2, 0, 0, 700, 700)
    assert response.status_code == 200
    user1_prof = rh.user_profile(user1["token"], user1["auth_user_id"]).json()["user"]
    response = requests.get(user1_prof["profile_img_url"])
    assert response.status_code == 200

def test_mulitple_users(clear, user1, user2, user3):
    response = rh.user_profile_uploadphoto(user1['token'], SAMPLE_JPEG_IMG_LINK, 0, 0, 700, 700)
    assert response.status_code == 200
    user1_prof = rh.user_profile(user1["token"], user1["auth_user_id"]).json()["user"]
    response = requests.get(user1_prof["profile_img_url"])
    assert response.status_code == 200

    response = rh.user_profile_uploadphoto(user2['token'], SAMPLE_JPEG_IMG_LINK, 0, 0, 700, 700)
    assert response.status_code == 200
    user2_prof = rh.user_profile(user2["token"], user2["auth_user_id"]).json()["user"]
    response = requests.get(user2_prof["profile_img_url"])
    assert response.status_code == 200

    response = rh.user_profile_uploadphoto(user3['token'], SAMPLE_JPEG_IMG_LINK2, 0, 0, 700, 700)
    assert response.status_code == 200
    user3_prof = rh.user_profile(user3["token"], user3["auth_user_id"]).json()["user"]
    response = requests.get(user3_prof["profile_img_url"])
    assert response.status_code == 200
