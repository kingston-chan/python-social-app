"""
Functions to:
- Send a message from the authorised user to the channel specified by channel_id.
- Given a message, update its text with new text.
- Given a message_id for a message, remove the message from the channel/DM.
"""
from src.error import InputError, AccessError
from src.data_store import data_store
import time

def message_send_v1(auth_user_id, channel_id, message):
    """
    Send a message from the authorised user to the channel specified by channel_id.

    Arguments: 
        auth_user_id (integer) - id of user sending the message
        channel_id (integer) - id of the channel the message is being posted on
        message (string) - the message itself

    Exceptions:
        InputError - Occurs when given:
                        - channel_id does not refer to a valid channel
                        - length of message is less than 1 or over 1000 characters
        AccessError - Occurs when channel_id is valid and the authorised user is not 
                        a member of the channel

    Return Value:
        Return a dictionary containing the message id on successful 
        creation of message

    """
    # Get variables from store
    store = data_store.get()
    channels = store["channels"]
    messages = store["channel_messages"]

    # Initialise new variables
    selected_channel = {}
    valid_channel = False
    valid_message = False

    # Locate channel
    for channel in channels:
        if channel['id'] == channel_id:
            valid_channel = True
            selected_channel = channel
    
    # Validates length of message
    if len(message) > 0 and len(message) < 1001:
        valid_message = True

    # If channel not found, InputError
    if not valid_channel:
        raise InputError(description="This channel is not valid.")
    # If message too short/long, InputError
    elif not valid_message:
        if len(message) < 1:
            raise InputError(description="This message is too short.")
        else:
            raise InputError(description="This message is too long.")
    
    # If user not in channel, InputError
    if auth_user_id not in selected_channel['all_members']:
        raise AccessError(description="This user is not a member of this channel.")

    # Increment message_id_gen
    store['message_id_gen'] += 1

    # Make up new message dictionary and append it in channel_messages list
    new_message = {
        'message_id': store['message_id_gen'],
        'u_id': auth_user_id,
        'channel_id': channel_id,
        'message': message,
        'shared_message': None,
        'time_created': int(time.time()),
    }
    messages.append(new_message)
    
    # Store data into data_store and return dictionary with the message_id
    data_store.set(store)
    return {
        'message_id': new_message['message_id']
    }

def message_edit_v1(auth_user_id, message_id, message):
    """
    Given a message, update its text with new text. 
    If new text is blank, the message is deleted.

    Arguments: 
        auth_user_id (integer) - id of user editing the message
        message_id (integer) - id of the message is being edited on
        message (string) - the new message

    Exceptions:
        InputError - Occurs when given:
                        - length of message is over 1000 characters
                        - message_id does not refer to a valid message within a 
                        channel/DM that the authorised user has joined
        AccessError - Occurs when message_id refers to a valid message in a 
                    joined channel/DM and none of the following are true:
                        - the message was sent by the authorised user making this request
                        - the authorised user has owner permissions in the channel/DM

    Return Value:
        Returns an empty dictionary

    """
    # Get variables from store
    store = data_store.get()
    channels = store["channels"]
    dms = store["dms"]
    channel_messages = store["channel_messages"]
    dm_messages = store["dm_messages"]

    # Initialise new variables
    selected_message = {}
    selected_channel = {}
    selected_dm = {}
    valid_message_id = False
    valid_message = False
    in_channel = False

    # Locate message in channels
    for target_message in channel_messages:
        if int(target_message['message_id']) == int(message_id):
            valid_message_id = True
            selected_message = target_message
            in_channel = True

    # Locate message in DMs
    for target_message in dm_messages:
        if int(target_message['message_id']) == int(message_id):
            valid_message_id = True
            selected_message = target_message

    # Validates length of message
    if len(message) < 1001:
        valid_message = True

    # If message not found, InputError
    if not valid_message_id:
        raise InputError(description="This message id is not valid.")
    # If message too long, InputError
    elif not valid_message:
        raise InputError(description="This message is too long.")

    # If message in channel
    if in_channel:
        # Locate channel        
        for channel in channels:
            if int(channel['id']) == int(selected_message['channel_id']):
                selected_channel = channel
        # If user not in channel, InputError
        if auth_user_id not in selected_channel['all_members']:
            raise InputError(description="This user is not a member of this channel.")
        # If user not in message and not an owner, AccessError
        elif auth_user_id is not selected_message['u_id'] and auth_user_id not in selected_channel['owner_permissions']:
            raise AccessError(description="This user is not allowed to edit this message.")
        
        # If message is empty, remove new message in located channel
        if message == "":
            channel_messages.remove(selected_message)
        # Else edit message in located channel
        else:
            selected_message['message'] = message
            

    # Else message should be in DM
    else: 
        # Locate DM
        for dm in dms:
            if int(dm['dm_id']) == int(selected_message['dm_id']):
                selected_dm = dm
        # If DM is deleted/invalid, Input Error
        if selected_dm == {}:
            raise InputError(description="This DM is invalid.")
        # If user not in DM, InputError
        if auth_user_id not in dm['members']:
            raise InputError(description="This user is not a member of this DM.")
        # If user not in DM and not an owner, AccessError
        elif auth_user_id is not selected_message['u_id'] and auth_user_id is not selected_dm['owner_of_dm']:
            raise AccessError(description="This user is not allowed to edit this DM message.")
        
        # If message is empty, remove new message in located DM
        if message == "":
            dm_messages.remove(selected_message)
        # Else edit message in located DM
        else:
            selected_message['message'] = message
    
    # Store data into data_store and return empty dictionary
    data_store.set(store)
    return {}

def message_remove_v1(auth_user_id, message_id):
    """
    Given a message, update its text with new text. 
    If new text is blank, the message is deleted.

    Arguments: 
        auth_user_id (integer) - id of user removing the message
        message_id (integer) - id of the message is being deleted

    Exceptions:
        InputError - Occurs when given:
                        - message_id does not refer to a valid message within 
                          a channel/DM that the authorised user has joined
        AccessError - Occurs when message_id refers to a valid message in a 
                      joined channel/DM and none of the following are true:
                        - the message was sent by the authorised user making this request
                        - the authorised user has owner permissions in the channel/DM

    Return Value:
        Returns an empty dictionary

    """
    # Get variables from store
    store = data_store.get()
    channels = store["channels"]
    dms = store["dms"]
    channel_messages = store["channel_messages"]
    dm_messages = store["dm_messages"]

    # Initialise new variables
    selected_message = {}
    selected_channel = {}
    selected_dm = {}
    valid_message_id = False
    in_channel = False

    # Locate message in channels
    for target_message in channel_messages:
        if int(target_message['message_id']) == int(message_id):
            valid_message_id = True
            selected_message = target_message
            in_channel = True

    # Locate message in DMs
    for target_message in dm_messages:
        if int(target_message['message_id']) == int(message_id):
            valid_message_id = True
            selected_message = target_message
    
    # If message not found, InputError
    if not valid_message_id:
        raise InputError(description="This message id is not valid.")

    # If message in channel
    if in_channel:
        # Locate channel
        for channel in channels:
            if int(channel['id']) == int(selected_message['channel_id']):
                selected_channel = channel
        # If user not in channel, InputError
        if auth_user_id not in selected_channel['all_members']:
            raise InputError(description="This user is not a member of this channel.")
        # If user not in message and not an owner, AccessError
        elif auth_user_id is not selected_message['u_id'] and auth_user_id not in selected_channel['owner_permissions']:
            raise AccessError(description="This user is not allowed to edit this message.")
        # Remove located message in located channel
        channel_messages.remove(selected_message)

    # Else message should be in DM
    else:
        # Locate DM
        for dm in dms:
            if int(dm['dm_id']) == int(selected_message['dm_id']):
                selected_dm = dm
        # If DM is deleted/invalid, Input Error
        if selected_dm == {}:
            raise InputError(description="This DM is invalid.")
        # If user not in DM, InputError
        if auth_user_id not in selected_dm['members']:
            raise InputError(description="This user is not a member of this DM.")
        # If user not in DM and not an owner, AccessError
        elif auth_user_id is not selected_message['u_id'] and auth_user_id is not selected_dm['owner_of_dm']:
            raise AccessError(description="This user is not allowed to edit this DM message.")
        # Remove located message in located DM
        dm_messages.remove(selected_message)

    # Store data into data_store and return empty dictionary
    data_store.set(store)
    return {}

def message_senddm_v1(auth_user_id, dm_id, message):
    """
    Send a message from the authorised user to the DM specified by dm_id.

    Arguments: 
        auth_user_id (integer) - id of user sending the DM message
        dm_id (integer) - id of the DM the message is being posted on
        message (string) - the message itself

    Exceptions:
        InputError - Occurs when given:
                        - dm_id does not refer to a valid dm
                        - length of message is less than 1 or over 1000 characters
        AccessError - Occurs when dm_id is valid and the authorised user is not 
                        a member of the DM

    Return Value:
        Return a dictionary containing the dm id on successful 
        creation of DM message

    """
    # Get variables from store
    store = data_store.get()
    dms = store["dms"]
    dm_messages = store["dm_messages"]

    # Initialise new variables
    selected_dm = {}
    valid_dm = False
    valid_message = False

    # Locate DM
    for dm in dms:
        if dm['dm_id'] == dm_id:
            valid_dm = True
            selected_dm = dm
    
    # Validates length of message
    if len(message) > 0 and len(message) < 1001:
        valid_message = True

    # If DM not found, InputError
    if not valid_dm:
        raise InputError(description="This DM is not valid.")
    # If message too short/long, InputError
    elif not valid_message:
        if len(message) < 1:
            raise InputError(description="This message is too short.")
        else:
            raise InputError(description="This message is too long.")

    # If user not in DM, InputError
    if auth_user_id not in selected_dm['members']:
        raise AccessError(description="This user is not a member of this DM.")

    # Increment message_id_gen
    store['message_id_gen'] += 1

    # Make up new message dictionary and append it in dm_messages list
    new_dm_message = {
        'message_id': store['message_id_gen'],
        'u_id': auth_user_id,
        'dm_id': dm_id,
        'message': message,
        'shared_message': None,
        'time_created': int(time.time()),
    }
    dm_messages.append(new_dm_message)
    
    # Store data into data_store and return dictionary with the message_id
    data_store.set(store)
    return {
        'message_id': new_dm_message['message_id']
    }

def message_share_v1(auth_user_id, og_message_id, message, channel_id, dm_id):
    store = data_store.get()
    channels = store["channels"]
    dms = store["dms"]
    channel_messages = store["channel_messages"]
    dm_messages = store["dm_messages"]

    members = None
    # 0 = Channel, 1 = DM
    channel_or_dm = None
    if channel_id != -1 and dm_id == -1:
        channel_or_dm = 0
        channel_exists = False
        for channel in channels:
            if channel_id == channel["id"]:
                members = channel["all_members"]
                channel_exists = True

        if not channel_exists:
            raise InputError(description="Channel does not exist")

    elif channel_id == -1 and dm_id != -1:
        channel_or_dm = 1
        dm_exists = False
        for dm in dms:
            if dm_id == dm["dm_id"]:
                members = dm["members"]
                dm_exists = True
    
        if not dm_exists:
            raise InputError(description="DM does not exist")

    else:
        raise InputError(description="Neither channel_id nor dm_id are -1")

    if auth_user_id not in members:
        raise AccessError(description="The authorised user has not joined the channel/DM they are trying to share the message to")
    
    og_message_id_exists = False
    og_message = None
    og_shared_message = None
    for channel_message in channel_messages:
        if og_message_id == channel_message["message_id"]:
            og_message_id_exists = True
            og_message = channel_message["message"]
            og_shared_message = channel_message["shared_message"]
    
    for dm_message in dm_messages:
        if og_message_id == dm_message["message_id"]:
            og_message_id_exists = True
            og_message = dm_message["message"]
            og_shared_message = dm_message["shared_message"]
    
    if not og_message_id_exists:
        raise InputError(description="Invalid message ID")
    
    if len(message) > 1000:
        raise InputError(description="Message is too long")
    elif message == None:
        message = ""
    
    store["message_id_gen"] += 1

    shared_message = None
    if og_shared_message == None:
        shared_message = "\n\n" + "\"\"\"\n" + og_message + "\n\"\"\""
    else:
        shared_message =  "\n\n" + "\"\"\"\n" + og_message + og_shared_message + "\n\"\"\""

    new_message = {
        'message_id': store['message_id_gen'],
        'u_id': auth_user_id,
        'message': message,
        'shared_message': shared_message,
        'time_created': int(time.time()),    
    }

    if channel_or_dm == 0:
        new_message["channel_id"] = channel_id
        channel_messages.append(new_message)

    elif channel_or_dm == 1:
        new_message["dm_id"] = dm_id
        dm_messages.append(new_message)

    data_store.set(store)

    return {
        "shared_message_id": store['message_id_gen']
    }
    


    
