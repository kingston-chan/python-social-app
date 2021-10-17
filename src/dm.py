from src.error import InputError, AccessError
from src.data_store import data_store

def dm_details_v1(auth_user_id, dm_id):
    store = data_store.get()
    users = store['users']
    dms = store['dms']

    dm_info = {}

    member_ids = None
    
    dm_exists = False
    for dm in dms:
        if dm["dm_id"] == dm_id:
            dm_exists = True
            member_ids = dm["members"]
            dm_info["name"] = dm["name"]

        
    if not dm_exists:
        raise InputError("DM does not exist")
    
    if auth_user_id not in member_ids:
        raise AccessError("User is not apart of the DM")
    
    for user in users:
        if user["id"] == auth_user_id:
            dm_info["members"] = user

    return dm_info