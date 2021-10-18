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

    user_id = int(user_id)
    store = data_store.get()
    users = store["users"]
    
    for u in users:
        if user_id == u["id"]:
            user_dict = {"u_id": user_id, "email": u["email"], "name_first": u["name_first"], "name_last": u["name_last"], "handle_str": u["handle"]}
            return user_dict
        
    raise InputError("u_id does not refer to a valid user")

def user_profile_setname_v1():
    pass