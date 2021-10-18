from src.error import InputError, AccessError
from src.data_store import data_store

def assign_user_info(user_data_placeholder):
    """Assigns the user information with the appropriate key names required in the spec"""
    return {
        'u_id': user_data_placeholder['id'],
        'email': user_data_placeholder['email'],
        'name_first': user_data_placeholder['name_first'],
        'name_last': user_data_placeholder['name_last'],
        'handle_str':user_data_placeholder['handle']
    }

def dm_create_v1(auth_user_id, u_ids):
    store = data_store.get()
    name_list= []

    owner_name = None

    new_dm_id = len(store["dms"]) + 1

    for users in u_ids:
        i = False
        for user in store["users"]:
            if auth_user_id == user["id"]:
                owner_name = user["handle"]

            if users == user["id"]:
                i = True
                if user["handle"] == None and user["email"] == None:
                    raise InputError("Invalid users") 
                else:
                    name_list.append(user["handle"])
        if i == False:
            raise InputError("Invalid users") 
   
    name_list.append(owner_name)
    name_list = sorted(name_list)

    i = 1
    name = name_list[0]
    while i  < len(name_list):
        name = name + ', ' + name_list[i]
        i += 1

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

def dm_messages_v1(auth_user_id, dm_id, start):
    """
    Given a DM with ID dm_id that the authorised user is a member of, return 
    up to 50 messages between index "start" and "start + 50".

    Arguments: 
        auth_user_id (integer) - ID of the member of the DM
        dm_id (integer) - ID of the DM
        start (integer) - The index number of the first message to be returned.

    Exceptions:
        InputError - Occurs when given:
                        - dm_id does not refer to a valid DM
                        - start is greater than the total number of 
                          messages in the DM

        AccessError - Occurs when given:
                        - dm_id is valid and the authorised user is not 
                          a member of the DM
        
    Return Values:
        Returns a dictionary of a list of DM messages from index["start"] to
        index["start+50"], the start value and the end value.
    
    """
# Checks if dm and start are valid inputs.
    dm_valid = False
    start_valid = False
    selected_dm = {}
    store = data_store.get()
    dms = store['dms']
    dm_messages = store['dm_messages']

    # Scans if the DM exists.
    for dm in dms:
        if dm['dm_id'] == dm_id:
            dm_valid = True
            # Checks if the start value is valid within the length of 
            # messages in the DM.
            if start <= len(list(filter(lambda x: (x['dm_id'] == dm_id), dm_messages))):
                start_valid = True
                selected_dm = dm  # DM is also selected

    # If the dm_id or start value are invalid, then errors are raised.
    if dm_valid is False:
        raise InputError("This dm is not valid.")
    if start_valid is False:
        raise InputError("This start is not valid.")
    
    # Checks if the authorised user is a member of the DM.
    member_valid = False
    for member in selected_dm['members']:
        if member == auth_user_id:
            member_valid = True

    # If the user is not a member, then an error is raised.
    if member_valid is False:
        raise AccessError('User is not authorised.')

    # The DM is scanned for its messages.
    filtered_dm_messages = []

    if dm_messages == []:
        length = 0
    else:
        filtered_dm_messages = list(filter(lambda x: (x['dm_id'] == dm_id), dm_messages))
        filtered_dm_messages.reverse()
        length = len(filtered_dm_messages)

    index = start
    counter = 0
    selected_dm_messages = []
    while index < length and counter < 50:
        selected_dm_message = filtered_dm_messages[index]
        dm_message_dict = {
            "message_id": selected_dm_message['message_id'],
            "u_id": selected_dm_message['u_id'],
            "message": selected_dm_message['message'],
            "time_created": selected_dm_message['time_created']
        }
        selected_dm_messages.append(dm_message_dict)
        index += 1
        counter += 1

    # If the scanner hits the end of the messages, the end is -1
    # else, the end is the final message index.
    if index == length:
        end = -1
    else:
        end = index

    # The selected messages, the start and the end values are returned.
    return {
        'messages': selected_dm_messages,
        'start': start,
        'end': end,
    }
