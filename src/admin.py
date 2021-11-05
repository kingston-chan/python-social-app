"""
Functions to:
- Remove user from streams, removes them from all channels and dms
- Change user's permission from member to global owner and global owner to member
"""

from src.data_store import data_store
from src.error import InputError, AccessError

def change_msg(msg, user_id):
    if msg["u_id"] == user_id:
        msg["message"] = "Removed user"
    return msg

def remove_from_dm(dm, user_id):
    if user_id in dm["members"]:
        dm["members"].remove(user_id)
    return dm

def remove_from_channel(channel, user_id):
    if user_id in channel["all_members"]:
        channel["all_members"].remove(user_id)
    if user_id in channel["owner_permissions"]:
        channel["owner_permissions"].remove(user_id)
    if user_id in channel["owner_members"]:
        channel["owner_members"].remove(user_id)
    return channel

def give_permissions(channel, user_id):
    if user_id in channel["all_members"] and user_id not in channel["owner_permissions"]:
        channel["owner_permissions"].append(user_id)
    return channel

def revoke_permissions(channel, user_id):
    if user_id in channel["owner_permissions"] and user_id not in channel["owner_members"]:
        channel["owner_permissions"].remove(user_id)
    return channel

def check_valid_user_and_owner(auth_user_id, u_id, users, permission=None):
    """Helper function to raise appropriate errors"""
    auth_id_user = list(filter(lambda user: (user["id"] == auth_user_id), users))
    uid_user = list(filter(lambda user: (user["id"] == u_id), users))
    global_owners = list(filter(lambda user: (user["permission"] == 1), users))

    # uid is invalid
    if len(uid_user) != 1:
        raise InputError(description="Invalid User")
    # uid belongs to removed user
    if uid_user[0]["email"] is None and uid_user[0]["handle"] is None:
        raise InputError(description="Removed User")
    # Auth user id is not a global owner
    if auth_id_user[0]["permission"] != 1:
        raise AccessError(description="Authorised user is not a global owner")

    if permission:
        # U_id refers to a user who is the only global owner
        if uid_user[0]["permission"] == 1 and len(global_owners) == 1 and permission == 2:
            raise InputError(description="Cannot demote only global owner")
    else:
        if uid_user[0]["permission"] == 1 and len(global_owners) == 1:
            raise InputError(description="Cannot remove only global owner")


def admin_userpermission_change_v1(auth_user_id, u_id, permission_id):
    """
    Given a user by their user ID, set their permissions to new permissions described by permission_id.

    Arguments:
        auth_user_id (int) - id of the authenticated user
        u_id (int) - id of the user being its permission changed
        permission_id (int) - id of the permission being assigned to the user, i.e. 1 for global owner
                              and 2 for member  

    Exceptions:
        InputError occurs when:
            - u_id does not refer to a valid user
            - u_id refers to user who is the only global owner and they are being demoted to a member
            - permission_id is invalid
        AccessError occurs when:
            - auth_user_id is not a global owner
    
    Return Value
        Returns an empty dictionary on successful user permission change
    """
    store = data_store.get()
    
    # Exceptions
    check_valid_user_and_owner(auth_user_id, u_id, store["users"], permission_id)
    # Check for invalid permission id
    if permission_id not in [1,2]:
        raise InputError(description="Invalid permission id")
    
    list(filter(lambda user: u_id == user["id"], store["users"]))[0]["permission"] = permission_id

    if permission_id == 1:
        store["channels"] = list(map(lambda channel: give_permissions(channel, u_id), store["channels"]))
    else:
        store["channels"] = list(map(lambda channel: revoke_permissions(channel, u_id), store["channels"]))
    
    data_store.set(store)
    return {}


def admin_user_remove_v1(auth_user_id, u_id):
    """
    Given a user by their u_id, remove them from the Streams. This means they should be removed from all 
    channels/DMs, and will not be included in the list of users returned by users/all. Streams owners can 
    remove other Streams owners (including the original first owner). Once users are removed, the contents 
    of the messages they sent will be replaced by 'Removed user'. Their profile must still be retrievable 
    with user/profile, however name_first should be 'Removed' and name_last should be 'user'. The user's 
    email and handle should be reusable.

    Arguments:
        auth_user_id (int) - id of the authenticated user
        u_id (int) - id of the user being removed

    Exceptions:
        InputError occurs when:
            - u_id does not refer to a valid user
            - u_id refers to a user who is the only global owner
        AccessError occurs when:
            - auth_user_id is not a global owner
    
    Return Value
        Returns an empty dictionary on successful user removal
    """
    store = data_store.get()
    
    check_valid_user_and_owner(auth_user_id, u_id, store["users"])
    
    # Remove user from all channels
    store["channels"] = list(map(lambda channel: remove_from_channel(channel, u_id), store["channels"]))
    # Remove user from all dms
    store["dms"] = list(map(lambda dm: remove_from_dm(dm, u_id), store["dms"]))
    # Change all removed user messages to "Removed user" 
    store["dm_messages"] = list(map(lambda msg: change_msg(msg, u_id), store["dm_messages"]))
    store["channel_messages"] = list(map(lambda msg: change_msg(msg, u_id), store["channel_messages"]))
    store["sessions"][u_id].clear()

    user = list(filter(lambda user: user["id"] == u_id, store["users"]))[0]
    user["email"] = None 
    user["password"] = None
    user["handle"] = None
    user["permission"] = None
    user["name_first"] = "Removed"
    user["name_last"] = "user"
    
    data_store.set(store)
    return {}


    

    