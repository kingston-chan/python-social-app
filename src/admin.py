"""
Functions to:
- Remove user from streams, removes them from all channels and dms
- Change user's permission from member to global owner and global owner to member
"""

from src.data_store import data_store
from src.error import InputError, AccessError

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
    users = store["users"]
    
    # Exceptions
    global_owners = list(filter(lambda user: (user["permission"] == 1), users))
    # Not a global owner
    if len(list(filter(lambda owner: (owner["id"] == auth_user_id), global_owners))) != 1:
        raise AccessError("Not global owner")
    user_being_changed = list(filter(lambda user: (user["id"] == u_id), users))
    # u_id does not belong to anyone on streams
    if len(user_being_changed) != 1:
        raise InputError("Invalid User")
    # u_id belongs to a removed user of streams
    if user_being_changed[0]["email"] is None and user_being_changed[0]["handle"] is None:
        raise InputError("Remove User")
    # u_id refers to only global owner
    if len(global_owners) == 1 and user_being_changed[0]["permission"] == 1:
        raise InputError("Only global owner left, cannot remove")
    # Invalid permission id
    if not permission_id in [1,2]:
        raise InputError("Invalid permission id")

    channels = store["channels"]
    
    if permission_id == 1:
        user_being_changed[0]["permission"] = 1
        for channel in channels:
            if u_id in channel["all_members"] and u_id not in channel["owner_permissions"]:
                channel["owner_permissions"].append(u_id)
     
    if permission_id == 2:
        user_being_changed[0]["permission"] = 2
        for channel in channels:
            if u_id in channel["owner_permissions"] and u_id not in channel["owner_members"]:
                channel["owner_permissions"].remove(u_id)
    
    data_store.set(store)
    return {}



    

    