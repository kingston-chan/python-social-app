"""
Functions to:
- Send a message from the authorised user to the channel specified by channel_id.
- Given a message, update its text with new text.
- Given a message_id for a message, remove the message from the channel/DM.
"""
from src.error import InputError, AccessError
from src.data_store import data_store
from src.user import users_stats_v1
from src.other import save
import time
import threading

def update_message(new_message, message_list, old_message):
    """Helper function for message edit"""
    # If message too long, InputError
    if len(new_message) > 1000:
        raise InputError(description="Invalid message length")
    # Remove channel message if empty message
    if new_message == "":
        message_list.remove(old_message)
    else:
        old_message["message"] = new_message

def pin_message(message):
    """Helper function to check if message is pinned, else pin it"""
    if message["is_pinned"]:
        raise InputError(description="Message is already pinned")
    message["is_pinned"] = True


def get_message(message_id, channel_messages, dm_messages):
    """Helper function to get message"""
    # Find channel/dm of og message
    channel_msg = list(filter(lambda message: message["message_id"] == message_id, channel_messages))
    dm_msg = list(filter(lambda message: message["message_id"] == message_id, dm_messages))
    return (channel_msg, dm_msg)

def react_message(message, reaction):
    """Helper function to create/append new reaction"""
    react = list(filter(lambda react: react["react_id"] == reaction[1], message["reacts"]))
    # Check if react id already exists
    if not react:
        message["reacts"].append({
            "react_id": reaction[1],
            "u_ids": [reaction[0]],
            "is_this_user_reacted": False
        })
    else:
        # Check if user already reacted with same react id
        if reaction[0] in react[0]["u_ids"]:
            raise InputError("User has already reacted")
        react[0]["u_ids"].append(reaction[0])

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
    messages = store["channel_messages"]

    valid_channel = list(filter(lambda channel: channel["id"] == channel_id, store["channels"]))
    # If channel not found, InputError
    if not valid_channel:
        raise InputError(description="This channel is not valid.")
    
    # If user not in channel, InputError
    if auth_user_id not in valid_channel[0]['all_members']:
        raise AccessError(description="This user is not a member of this channel.")
    
    # Validates length of message
    # If message too short/long, InputError
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="This message length is invalid.")

    # Increment message_id_gen
    store['message_id_gen'] += 1

    # Make up new message dictionary and append it in channel_messages list
    new_message = {
        'message_id': store['message_id_gen'],
        'u_id': auth_user_id,
        'channel_id': channel_id,
        'message': message,
        'time_created': int(time.time()),
        'reacts': [],
        'is_pinned': False
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

    # Locate message in channels
    valid_channel_msg = list(filter(lambda msg: msg["message_id"] == message_id, store["channel_messages"]))
    # Locate message in DMs
    valid_dm_msg = list(filter(lambda msg: msg["message_id"] == message_id, store["dm_messages"]))
    # Message belongs to a channel
    if valid_channel_msg:
        # There must be a channel that contains this message if message_id is valid
        valid_channel = list(filter(lambda channel: channel["id"] == valid_channel_msg[0]["channel_id"], store["channels"]))[0]
        if auth_user_id not in valid_channel["all_members"]:
            raise InputError(description="This user is not a member of this channel.")
        if auth_user_id != valid_channel_msg[0]["u_id"] and auth_user_id not in valid_channel["owner_permissions"]:
            raise AccessError(description="This user is not allowed to edit this message.")        
        update_message(message, store["channel_messages"], valid_channel_msg[0])
    elif valid_dm_msg:
        # There must be a dm that contains this message if message_id is valid
        valid_dm = list(filter(lambda dm: dm["dm_id"] == valid_dm_msg[0]["dm_id"], store["dms"]))[0]
        if auth_user_id not in valid_dm["members"]:
            raise InputError(description="This user is not a member of this DM.")
        if auth_user_id != valid_dm_msg[0]["u_id"] and auth_user_id != valid_dm["owner_of_dm"]:
            raise AccessError(description="This user is not allowed to edit this message.")        
        update_message(message, store["dm_messages"], valid_dm_msg[0])
    else:
        raise InputError("Invalid message id")
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

    # Locate message in channels
    valid_channel_msg = list(filter(lambda msg: msg["message_id"] == message_id, store["channel_messages"]))
    # Locate message in DMs
    valid_dm_msg = list(filter(lambda msg: msg["message_id"] == message_id, store["dm_messages"]))
    # Message belongs to a channel
    if valid_channel_msg:
        # There must be a channel that contains this message if message_id is valid
        valid_channel = list(filter(lambda channel: channel["id"] == valid_channel_msg[0]["channel_id"], store["channels"]))[0]
        if auth_user_id not in valid_channel["all_members"]:
            raise InputError(description="This user is not a member of this channel.")
        if auth_user_id != valid_channel_msg[0]["u_id"] and auth_user_id not in valid_channel["owner_permissions"]:
            raise AccessError(description="This user is not allowed to remove this message.")
        store["channel_messages"].remove(valid_channel_msg[0])
    elif valid_dm_msg:
        # There must be a dm that contains this message if message_id is valid
        valid_dm = list(filter(lambda dm: dm["dm_id"] == valid_dm_msg[0]["dm_id"], store["dms"]))[0]
        if auth_user_id not in valid_dm["members"]:
            raise InputError(description="This user is not a member of this DM.")
        if auth_user_id != valid_dm_msg[0]["u_id"] and auth_user_id != valid_dm["owner_of_dm"]:
            raise AccessError(description="This user is not allowed to remove this message.")
        store["dm_messages"].remove(valid_dm_msg[0])
    else:
        raise InputError("Invalid message id")
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
    dm_messages = store["dm_messages"]

    # Locate DM
    valid_dm = list(filter(lambda dm: dm["dm_id"] == dm_id, store["dms"]))

    # If DM not found, InputError
    if not valid_dm:
        raise InputError(description="This DM is not valid.")
    
    # If user not in DM, InputError
    if auth_user_id not in valid_dm[0]['members']:
        raise AccessError(description="This user is not a member of this DM.")
    
    # Validates length of message
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="This message length is invalid.")

    # Increment message_id_gen
    store['message_id_gen'] += 1

    # Make up new message dictionary and append it in dm_messages list
    new_dm_message = {
        'message_id': store['message_id_gen'],
        'u_id': auth_user_id,
        'dm_id': dm_id,
        'message': message,
        'time_created': int(time.time()),
        'reacts': [],
        'is_pinned': False,
    }
    dm_messages.append(new_dm_message)
    
    # Store data into data_store and return dictionary with the message_id
    data_store.set(store)
    return {
        'message_id': new_dm_message['message_id']
    }

def message_pin_v1(auth_user_id, message_id):
    """
    Given a message within a channel or DM, mark it as "pinned".

    Arguments: 
        auth_user_id (integer) - id of user pinning the message
        message_id (integer) - id of the message is being pinned

    Exceptions:
        InputError - Occurs when given:
                        - message_id does not refer to a valid message within 
                          a channel/DM that the authorised user has joined
                        - the message is already pinned
        AccessError - Occurs when:
                        - message_id refers to a valid message in a joined 
                          channel/DM and the authorised user does not have owner 
                          permissions in the channel/DM.

    Return Value:
        Returns an empty dictionary

    """
    # Get variables from store
    store = data_store.get()
    
    # Locate message in channels
    valid_channel_msg = list(filter(lambda msg: msg["message_id"] == message_id, store["channel_messages"]))
    # Locate message in DMs
    valid_dm_msg = list(filter(lambda msg: msg["message_id"] == message_id, store["dm_messages"]))

    # If message in channel
    if valid_channel_msg:
        # Locate channel
        valid_channel = list(filter(lambda channel: channel["id"] == valid_channel_msg[0]["channel_id"], store["channels"]))[0]
        # If user not in channel, InputError
        if auth_user_id not in valid_channel['all_members']:
            raise InputError(description="This user is not a member of this channel.")
        # If user not in message and not an owner, AccessError
        if auth_user_id not in valid_channel['owner_permissions']:
            raise AccessError(description="This user is not allowed to pin this message.")
        pin_message(valid_channel_msg[0])
    elif valid_dm_msg:
        # Locate DM
        valid_dm = list(filter(lambda dm: dm["dm_id"] == valid_dm_msg[0]["dm_id"], store["dms"]))[0]
        # If user not in DM, InputError
        if auth_user_id not in valid_dm['members']:
            raise InputError(description="This user is not a member of this DM.")
        # If user not in DM and not an owner, AccessError
        if auth_user_id is not valid_dm['owner_of_dm']:
            raise AccessError(description="This user is not allowed to pin this DM message.")
        # Pin located message in located DM
        pin_message(valid_dm_msg[0])
    else:
        # If message not found, InputError
        raise InputError(description="This message id is not valid.")
    # Store data into data_store and return empty dictionary
    data_store.set(store)
    return {}

def message_sendlaterdm_threading(auth_user_id, dm_id, message, time_sent, message_id):
    store = data_store.get()
    dm_messages = store['dm_messages']

    new_message = {
        "message_id": message_id,
        "u_id": auth_user_id,
        'dm_id': dm_id,
        'message': message,
        'time_created': time_sent,   
        'reacts': [],
        'is_pinned': False,
    }

    dm_messages.append(new_message)
    users_stats_v1()
    data_store.set(store)
    save()

def message_sendlaterdm_v1(auth_user_id, dm_id, message, time_sent):
    store = data_store.get()
    time_now = time.time()
    time_difference = int(time_sent - time_now)
    valid_dm = list(filter(lambda dm: dm["dm_id"] == dm_id, store['dms']))
    # Check if valid dm id
    if not valid_dm:
        raise InputError(description="dm doesn't exist")
    # Check if user is part of dm
    if auth_user_id not in valid_dm[0]["members"]:
        raise AccessError(description="User is not apart of the dm")
    # Check valid message length
    if len(message) > 1000:
        raise InputError(description="Message is too long")
    # Check if time_send is a time in the past
    if time_difference < 0:
        raise InputError(description="Time set is in the past")
    
    store['message_id_gen'] += 1

    x = threading.Timer(time_difference, message_sendlaterdm_threading, args=(auth_user_id, dm_id, message, time_sent, store['message_id_gen']))

    x.start()

    return {
        "message_id": store['message_id_gen']
    }

def message_sendlater_threading(auth_user_id, channel_id, message, time_sent, message_id):
    store = data_store.get()
    channel_messages = store['channel_messages']

    new_message = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'channel_id': channel_id,
        'message': message,
        'time_created': time_sent,
        'reacts': [],
        'is_pinned': False,   
    }

    channel_messages.append(new_message)
    users_stats_v1()
    data_store.set(store)
    save()

def message_sendlater_v1(auth_user_id, channel_id, message, time_sent):
    store = data_store.get()
    channels = store['channels']
    
    time_now = time.time()
    time_difference = int(time_sent - time_now)

    valid_channel = list(filter(lambda channel: channel["id"] == channel_id, channels))
        
    if not valid_channel:
        raise InputError(description="Channel doesn't exist")

    if auth_user_id not in valid_channel[0]["all_members"]:
        raise AccessError(description="User is not apart of the channel")

    if time_difference < 0:
        raise InputError(description="Time set is in the past")
    
    if len(message) > 1000:
        raise InputError(description="Message is too long")
 
    store['message_id_gen'] += 1

    x = threading.Timer(time_difference, message_sendlater_threading, args=(auth_user_id, channel_id, message, time_sent, store['message_id_gen']))

    x.start()

    return {
        "message_id": store["message_id_gen"]
    }

def message_share_v1(auth_user_id, og_message_id, message, channel_id, dm_id):
    store = data_store.get()
    channel_messages = store["channel_messages"]
    dm_messages = store["dm_messages"]

    valid_channel = list(filter(lambda channel: channel["id"] == channel_id, store["channels"]))
    valid_dm = list(filter(lambda dm: dm["dm_id"] == dm_id, store["dms"]))
    # Check if both channel/dm id are invalid
    if not valid_channel and not valid_dm:
        raise InputError(description="Channel/DM does not exist")
    # Check if both channel/dm id are valid i.e. neither channel_id nor dm_id are -1
    if valid_channel and valid_dm:
        raise InputError(description="Neither channel_id nor dm_id are -1")
    # Check if user is in channel/dm given that one of them is valid
    if auth_user_id not in (valid_channel[0]["all_members"] if valid_channel else valid_dm[0]["members"]):
        raise AccessError(description="The authorised user has not joined the channel/DM they are trying to share the message to")
    valid_og_message = get_message(og_message_id, channel_messages, dm_messages)
    # Message id does not refer to any message id
    if valid_og_message == ([], []):
        raise InputError(description="Message ID does not refer to a valid message within a channel/dm user has joined")
    valid_og_message = valid_og_message[0][0] if valid_og_message[0] else valid_og_message[1][0]
    # Check for the message id refers to a valid message that refers to a message within a channel/dm the auth_user has joined
    if "channel_id" in valid_og_message:
        channel_og_message = list(filter(lambda channel: channel["id"] == valid_og_message["channel_id"], store["channels"]))[0]
        if auth_user_id not in channel_og_message["all_members"]:
            raise InputError(description="Message ID does not refer to a valid message within a channel/dm user has joined")
    else:
        dm_og_message = list(filter(lambda dm: dm["dm_id"] == valid_og_message["dm_id"], store["dms"]))[0]
        if auth_user_id not in dm_og_message["members"]:
            raise InputError(description="Message ID does not refer to a valid message within a channel/dm user has joined")
    
    if len(message) > 1000:
        raise InputError(description="Message is too long")

    store["message_id_gen"] += 1
    og_message = valid_og_message["message"]
    shared_message = f"{message}\n\n\"\"\"\n{og_message}\n\"\"\""
    new_message = {
        'message_id': store['message_id_gen'],
        'u_id': auth_user_id,
        'message': shared_message,
        'time_created': int(time.time()),    
        'reacts': [],
        'is_pinned': False,
    }

    if valid_channel:
        new_message["channel_id"] = channel_id
        channel_messages.append(new_message)
    else:
        new_message["dm_id"] = dm_id
        dm_messages.append(new_message)

    data_store.set(store)

    return {
        "shared_message_id": store['message_id_gen']
    }

def message_react_v1(auth_user_id, message_id, react_id):
    
    store = data_store.get()
    reaction = (auth_user_id, react_id)
    # Find message
    dm_message = list(filter(lambda msg: message_id == msg["message_id"], store["dm_messages"]))
    channel_message = list(filter(lambda msg: message_id == msg["message_id"], store["channel_messages"]))

    if react_id != 1:
        raise InputError("Invalid react ID")        
    
    if channel_message:
        # If channel message is valid then channel must be valid
        channel = list(filter(lambda channel: channel_message[0]["channel_id"] == channel["id"], store["channels"]))[0]
        # Check if message id refers to a channel message such that user has joined that channel
        if auth_user_id not in channel["all_members"]:
            raise InputError("Not Authorised User")
        react_message(channel_message[0], reaction)
    elif dm_message:
        # If dm_message is valid then dm must be valid
        dm = list(filter(lambda dm: dm_message[0]["dm_id"] == dm["dm_id"], store["dms"]))[0]
        # Check if message id refers to a dm message such that user has joined that dm
        if auth_user_id not in dm["members"]:
            raise InputError("Not Authorised User")
        react_message(dm_message[0], reaction)
    else:
        raise InputError("Not a valid message ID")
            
    return {}
