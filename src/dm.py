from src.error import InputError, AccessError
from src.data_store import data_store
from src.user import users_stats_v1

def assign_user_info(user_data_placeholder):
    """Assigns the user information with the appropriate key names required in the spec"""
    return {
        'u_id': user_data_placeholder['id'],
        'email': user_data_placeholder['email'],
        'name_first': user_data_placeholder['name_first'],
        'name_last': user_data_placeholder['name_last'],
        'handle_str':user_data_placeholder['handle']
    }

def output_dm(dm):
    """Change to required dm output format"""
    return {
        "name": dm["name"],
        "dm_id": dm["dm_id"]
    }

def dm_id_count():
    """Generate dm id"""
    store = data_store.get()
    store["dm_id_gen"] += 1
    dms_id = store["dm_id_gen"]
    data_store.set(store)
    return dms_id

def remove_msg(msg, dm_id):
    """Helper function to remove msgs when removing dm"""
    users_stats_v1()
    if msg["dm_id"] != dm_id:
        return True
    return False

def valid_user(user):
    """Check if removed user"""
    return user["email"] and user["handle"]

def dm_create_v1(auth_user_id, u_ids):
    '''
    This function creates a dm with the user with the inputted token bieng the owener of the dm and the list of user ids including members of the dm 
    Arguements
        -auth_user_id (integer)
        -a list of user ids that the dm is bieng created with (list of integers)
    Exception 
        - InputError => when any of user id's in the list of ids is invalid i.e. does not valid user
    return value 
        - empty list ==> {} 
    '''
    store = data_store.get()
    if auth_user_id not in u_ids:
        u_ids.append(auth_user_id)
    # Check if ids are valid
    users = list(filter(lambda user: user["id"] in u_ids and valid_user(user), store["users"]))

    if len(users) != len(u_ids):
        raise InputError(description="Invalid users")

    new_dm_id = dm_id_count()

    new_dm = {
        'name': ', '.join(sorted([user["handle"] for user in users])),
        'dm_id': new_dm_id,
        'owner_of_dm' : auth_user_id,
        'members': u_ids
    }

    store["dms"].append(new_dm)
    data_store.set(store)

    return {"dm_id" : new_dm_id}

def dm_leave_v1(auth_user_id, dm_id):
    """
    If the authorised user is a member of the DM of "dm_id", 
    remove the user as a member of the DM.

    Arguments:
        auth_user_id (integer) - ID of the user requesting to leave the DM.
        dm_id (integer) - ID of the DM requested for DM details.
    
    Exceptions:
        InputError - Occurs when dm_id does not refer to a valid DM.
        AccessError - Occurs when dm_id is valid but the authorised user is
        not a member of the DM.
    
    Return Value:
        Returns an empty dictionary upon success.
    """

    store = data_store.get()

    valid_dm = list(filter(lambda dm: dm["dm_id"] == dm_id, store["dms"]))

    if not valid_dm:
        raise InputError(description="DM does not exist")

    if auth_user_id not in valid_dm[0]["members"]:
        raise AccessError(description="User is not apart of the DM")

    # Removes the member from the members_list.
    valid_dm[0]["members"].remove(auth_user_id)
    
    data_store.set(store)
    
    return {}

def dm_details_v1(auth_user_id, dm_id):
    """
    If the authorised user is a member of the DM of "dm_id", 
    provide basic details about the DM.

    Arguments:
        auth_user_id (integer) - ID of the user requesting for DM details.
        dm_id (integer) - ID of the DM requested for DM details.
    
    Exceptions:
        InputError - Occurs when dm_id does not refer to a valid DM.
        AccessError - Occurs when dm_id is valid but the authorised user is
        not a member of the DM.
    
    Return Value:
        Returns a dictionary containing:
            - name (string)
            - members (list of dictionaries)
        The list of dictionaries contains the following:
            - u_id (integer)
            - email (string)
            - name_first (string)
            - name_last (string)
            - handle_str (string)
    """
    store = data_store.get()
    
    valid_dm = list(filter(lambda dm: dm["dm_id"] == dm_id, store["dms"]))
    # Check if valid dm_id
    if not valid_dm:
        raise InputError(description="DM does not exist")
    # If dm id is valid, check if auth_user_id is part of dm
    if auth_user_id not in valid_dm[0]["members"]:
        raise AccessError(description="User is not apart of the DM")
    
    # List of the members info
    users = list(filter(lambda user: user["id"] in valid_dm[0]["members"], store["users"]))

    return {
        "name": valid_dm[0]["name"],
        # Grabs the member's info and assigns it to the dictionary.
        "members": list(map(assign_user_info, users))
    }

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
    # Checks if DM and start are valid inputs.
    store = data_store.get()

    # If the dm_id or start value are invalid, then errors are raised.
    valid_dm = list(filter(lambda dm: dm["dm_id"] == dm_id, store["dms"]))
    if not valid_dm:
        raise InputError(description="This DM is not valid.")
    valid_msgs = list(filter(lambda msg: msg['dm_id'] == dm_id, store["dm_messages"]))
    if start > len(valid_msgs):
        raise InputError(description="This start is not valid.")
    
    # Checks if the authorised user is a member of the DM.
    # If the user is not a member, then an error is raised.
    if auth_user_id not in valid_dm[0]["members"]:
        raise AccessError(description='User is not authorised.')

    valid_msgs.reverse()

    # The selected messages, the start and the end values are returned.
    return {
        'messages': valid_msgs[start:start+50] if len(valid_msgs) >= start+50 else valid_msgs[start:],
        'start': start,
        'end': start+50 if start+50 < len(valid_msgs) else -1
    }

def dm_list_v1(auth_user_id):
    '''
    Return a list of dms that the the user belongs to where the user is passed as a token through the function

    Arguement
        - auth_user_id (integer) 
    Return value
        - returns a list dictionaries of dm's in the form of 
                {"dms" : [{"dm_id" : xxxxx, "name" : yyyyy}]}
                where 'dm_id' is a number and 'name' is a alphanumneric string 
    '''
    dm_list = filter(lambda dm: auth_user_id in dm["members"], data_store.get()["dms"])
    return {"dms" : list(map(output_dm, dm_list))}

def dm_remove_v1(auth_user_id, dm_id):
    '''
    Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.

    Aurgurments
        - auth_user_id (integer)
        - dm_id (integer)
    Exceptions
        - InputError => when any of dm_id is not a valid id, the dm of that id does not exist or a wrong type of input i.e. string 
        -AccessError => when dm_id is valid and the authorised user is not the original DM creator
    return value 
        -empty list ==>{}
    '''
    store = data_store.get()

    valid_dm = list(filter(lambda dm: dm["dm_id"] == dm_id, store["dms"]))

    # Check if dm_id is valid
    if not valid_dm:
        raise InputError(description="DM does not exist")
    # Check if auth_user_id is owner
    if valid_dm[0]["owner_of_dm"] != auth_user_id:
        raise AccessError(description="Not owner of DM")

    store["dms"].remove(valid_dm[0])
    store["dm_messages"] = list(filter(lambda msg: remove_msg(msg, dm_id), store["dm_messages"]))
    users_stats_v1()
    data_store.set(store)
    return {}



    
