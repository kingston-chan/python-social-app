"""
Functions to:
- List all users from the data store
- Return the profile of a given user_id
- Update authorised user's first and last name
- Update the authorised user's email address
- Update the authorised user's handle (i.e. display name)
"""

from src.data_store import data_store
from src.channel import assign_user_info
from src.error import InputError
import re, time
import urllib.request
import urllib.error
from PIL import Image
from src.config import url


def list_all_users():
    """
    List all users from the data store

    Arguments:
        None

    Exceptions:
        None
    
    Return Value
        Returns a list of dictionaries containing information about all Stream users.
        Each dictionary contains the user's id, email, first and last name and their 
        handle given that their email and handle is not None. 
    """
    store = data_store.get()
    users = store["users"]
    user_list = []
    for user in users:
        if user["email"] is not None and user["handle"] is not None:
            user_list.append(assign_user_info(user))
    return { "users": user_list }

def user_profile_v1(user_id):
    """
    Return the user info of the given user_id

    Arguments:
        user_id

    Exceptions:
        InputError when the user_id doesn't refer to a valid user
    
    Return Value
        Returns a dictionary containing the following user information:
        - u_id
        - email
        - name_first
        - name_last
        - handle_str
    """

    user_id = int(user_id)
    store = data_store.get()
    users = store["users"]
    
    for u in users:
        if user_id == u["id"]:
            user_dict = {"u_id": user_id, "email": u["email"], "name_first": u["name_first"], "name_last": u["name_last"], "handle_str": u["handle"]}
            return user_dict
        
    raise InputError(description="u_id does not refer to a valid user")

def user_profile_setname_v1(user_id, first_name, last_name):
    """
    Change the first and last name of the user given by user_id to the given names given by first_name and last_name

    Arguments:
        user_id, first_name, last_name

    Exceptions:
        InputError when the first or last name are too long or short
    
    Return Value
        Doesn't return a value
        Updates the data_store with the new first and last name
    """
    store = data_store.get()
    users = store["users"]

    if not 1 <= len(first_name) <= 50 or not 1 <= len(last_name) <= 50:
        raise InputError(description="Name length is too long or short")
    
    for u in users:
        if user_id == u["id"]:
            u["name_first"] = first_name
            u["name_last"] = last_name
    
    store["users"] = users
    data_store.set(store)

def user_profile_setemail_v1(user_id, user_email):
    """
    Change the email of the user given by user_id to the email given by user_email

    Arguments:
        user_id, user_email

    Exceptions:
        InputError when the email doesn't follow the specified format
    
    Return Value
        Doesn't return a value
        Updates the data_store with the new email
    """

    store = data_store.get()
    users = store["users"]

    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', user_email):
        raise InputError(description="Email is an invalid format")
    
    if dict_search(user_email, users, 'email'):
        raise InputError(description='Email is already being used by another user')


    for u in users:
        if user_id == u["id"]:
            u["email"] = user_email
            
    
    store["users"] = users
    data_store.set(store)

def user_profile_sethandle_v1(auth_user_id, handle_str):
    '''
    Update the authorised user's handle (i.e. display name)
    Arguements
        - auth-user_id (integer)
        - handle_str (string)
    Excpetions
        -InputError ==> length of handle_str is not between 3 and 20 characters inclusive
        -InputError ==> handle_str contains characters that are not alphanumeric
        -InputError ==> the handle is already used by another user
    return type
        - empty list 
    '''
    store = data_store.get()
    for user in store["users"]:
        if user["handle"] == handle_str:
            raise InputError(description="Handle already being used")
        if len(handle_str) > 20 or len(handle_str) < 3:
            raise InputError(description="Handle is not valid")
    if handle_str.isalnum():
        for user in store["users"]:
            if auth_user_id == user["id"]:
                user["handle"] = handle_str
    else:
        raise InputError(description="invalid string")
    return{}

def user_profile_uploadphoto_v1(auth_user_id, img_url, x_start, y_start, x_end, y_end):
    store = data_store.get()
    users = store["users"]
    img_count = store["img_count"]
    
    login_user = list(filter(lambda user: user["id"] == auth_user_id, users))

    if not img_url.endswith(".jpeg") and not img_url.endswith(".jpg"):
        raise InputError("Image uploaded not a JPG.")

    image_string = f"./imgurl/{img_count}.jpg"

    try:
        urllib.request.urlretrieve(img_url, image_string)
    except Exception:
        raise InputError("img_url returning HTTP status other than 200.") from InputError

    im = Image.open(image_string)
    print(im.size)
    max_y, max_x = im.size

    if x_start < 0 or x_start > max_x:
        raise InputError("Invalid x_start.")
    else:
        if x_end < 0 or x_end > max_x or x_end < x_start:
            raise InputError("Invalid x_end.")  

    if y_start < 0 or y_start > max_y:
        raise InputError("Invalid y_start.")
    else:
        if y_end < 0 or y_end > max_y or y_end < y_start:
            raise InputError("Invalid y_end.")    
    
    cropped = im.crop((x_start, y_start, x_end, y_end))
    cropped.save(image_string)
    login_user[0]['profile_img_url'] = f"{url}/imgurl/{img_count}.jpg"
    print(login_user[0]['profile_img_url'])
    store["img_count"] += 1
    data_store.set(store)

def users_stats_v1():
    """
    Updates the required statistics about the use of UNSW Streams.

    Arguments:
        None

    Exceptions:
        None
    
    Return Value
        None
    """
    store = data_store.get()
    
    # Find the number of users that are in at least 1 channel or dm
    num_users_in_channel_dm = 0
    for user in store["users"]:
        user_channels = len(list(filter(lambda channel: (user["id"] in channel["all_members"]), store["channels"])))
        user_dms = len(list(filter(lambda dm: (user["id"] in dm["members"]), store["dms"])))
        if user_channels or user_dms:
            num_users_in_channel_dm += 1

    # Find the number of valid users, i.e. non-deleted users
    valid_users = len(list(filter(lambda user: (user["email"] and user["handle"]), store["users"])))
    # Utilization rate: if no valid users, 0 else defined by num_users_in_channel_dm divided by valid_users
    store["metrics"]["utilization_rate"] = num_users_in_channel_dm/valid_users

    # Checks if each metric has at least 1 entry
    if store["metrics"]["channels_exist"] and store["metrics"]["dms_exist"] and store["metrics"]["messages_exist"]:
        # Number of channels changed
        metric_changed("channels_exist", len(store["channels"]), store)
        # Number of dms changed
        metric_changed("dms_exist", len(store["dms"]), store)
        # Number of messages changed
        metric_changed("messages_exist", len(store["channel_messages"]) + len(store["dm_messages"]), store)
    else:
        # First user registered, no registered use
        init_metrics("channels_exist", store)
        init_metrics("dms_exist", store)
        init_metrics("messages_exist", store)

def metric_changed(metric, metric_num, store):
    """Helper function to check metric and append new timestamp if changed"""
    if store["metrics"][metric][-1][f"num_{metric}"] != metric_num:
        store["metrics"][metric].append({
            f"num_{metric}": metric_num,
            "time_stamp": int(time.time())
        })
        data_store.set(store)

def init_metrics(metric, store):
    """Helper function to initialise metrics"""
    store["metrics"][metric].append({
        f"num_{metric}": 0,
        "time_stamp": int(time.time())
    })
    data_store.set(store)

def dict_search(item, users, item_name):
    for u in users:
        if u[item_name] == item:
            return 1
