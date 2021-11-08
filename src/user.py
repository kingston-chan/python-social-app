"""
Functions to:
- List all users from the data store
- Return the profile of a given user_id
- Update authorised user's first and last name
- Update the authorised user's email address
- Update the authorised user's handle (i.e. display name)
- Track the Streams workspace stats
"""

from src.data_store import data_store
from src.channel import assign_user_info
from src.error import InputError
import re, time

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

def is_in_channel_dm(user, channels, dms):
    """Helper function to determine if user is at least in a channel or not"""
    user_channels = len(list(filter(lambda channel: (user["id"] in channel["all_members"]), channels)))
    user_dms = len(list(filter(lambda dm: (user["id"] in dm["members"]), dms)))
    return bool(user_channels or user_dms)

def change_email(user, user_id, email):
    """Helper function to change user_id's email"""
    if user["id"] == user_id:
        user["email"] = email
    return user

def change_handle(user, user_id, handle):
    """Helper function to change user_id's handle"""
    if user["id"] == user_id:
        user["handle"] = handle
    return user

def output_user(user):
    if user["email"] is not None and user["handle"] is not None:
        return assign_user_info(user)

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
    # Maps all valid users with correct output, then filter None values i.e. removed users
    return { "users": list(filter(None, map(output_user, data_store.get()["users"]))) }

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
    # Find user corresponding to user_id
    valid_user = list(filter(lambda user: int(user_id) == user["id"], data_store.get()["users"]))
    if valid_user:
        return assign_user_info(valid_user[0])
    # Invalid user_id
    raise InputError("Invalid user")

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
    # Raise appropriate errors
    if not 1 <= len(first_name) <= 50 or not 1 <= len(last_name) <= 50:
        raise InputError(description="Name length is too long or short")
    # Find user corresponding to user_id
    user = list(filter(lambda user: user_id == user["id"], store["users"]))[0]
    user["name_first"] = first_name
    user["name_last"] = last_name
    
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
    # Raise appropriate errors
    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', user_email):
        raise InputError(description="Email is an invalid format")
    if list(filter(lambda user: user["email"] == user_email, users)):
        raise InputError(description='Email is already being used by another user')        
    # Change email of user_id
    store["users"] = list(map(lambda user: change_email(user, user_id, user_email), users))
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
    # Raise appropriate errors
    if len(handle_str) > 20 or len(handle_str) < 3 or not handle_str.isalnum():
        raise InputError(description="Handle is not valid")
    if list(filter(lambda user: user["handle"] == handle_str, store["users"])):
        raise InputError(description="Handle already being used")
    # Change handle of auth_user_id
    store["users"] = list(map(lambda user: change_handle(user, auth_user_id, handle_str), store["users"]))
    data_store.set(store)
    return {}

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
    users = store["users"]
    channels = store["channels"]
    dms = store["dms"]
    # Go through each user, check if in a channel/dm or not
    num_users_in_channel_dm = len(list(filter(lambda user: is_in_channel_dm(user, channels, dms), users)))

    # Find the number of valid users, i.e. non-deleted users
    valid_users = len(list(filter(lambda user: (user["email"] and user["handle"]), users)))
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



    
