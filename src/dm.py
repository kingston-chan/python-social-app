from src.error import InputError, AccessError
from src.data_store import data_store

def dm_create_v1(auth_user_id, u_ids):
    store = data_store.get()
    name_list= []

    new_dm_id = len(store["dms"]) + 1

    for users in u_ids:
        i = False
        for user in store["users"]:
            if users == user["id"]:
                i = True
                if user["handle"] == None and user["email"] == None:
                    raise InputError("Invalid users") 
                else:
                    name_list.append(user["handle"])
        if i == False:
            raise InputError("Invalid users") 
   
   
    name_list = sorted(name_list)

    i = 1
    name = name_list[0]
    while i  < len(name_list):
        name = name + ', ' + name_list[i]

    u_ids.append(auth_user_id)

    new_dm = {
        'name': name,
        'dm_id': new_dm_id,
        'owner_of_dm' : auth_user_id,
        'members': u_ids
    }

    store["dms"].append(new_dm)
    data_store.set(store)

    return {"dm_id" : new_dm_id}

def dm_details_v1(auth_user_id, dm_id):
    store = data_store.get()
    users = store['users']
    dms = store['dms']

    dm_info = {}
    user_info = {}

    member_ids = None
    
    dm_exists = False
    for dm in dms:
        if dm["dm_id"] == dm_id:
            dm_exists = True
            member_ids = dm["members"]
            dm_info["name"] = dm["name"]
            dm_info["members"] = []
        
    if not dm_exists:
        raise InputError("DM does not exist")
    
    if auth_user_id not in member_ids:
        raise AccessError("User is not apart of the DM")
    
    for user in users:
        if user["id"] in member_ids:
            user_info = assign_user_info(user)
            dm_info["members"].append(user_info)

    return dm_info


def assign_user_info(user_data_placeholder):
    """Assigns the user information with the appropriate key names required in the spec"""
    return {
        'u_id': user_data_placeholder['id'],
        'email': user_data_placeholder['email'],
        'name_first': user_data_placeholder['name_first'],
        'name_last': user_data_placeholder['name_last'],
        'handle_str':user_data_placeholder['handle']
    }