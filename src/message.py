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

CHANNEL = 1
DM = 2

                                        ###################################
                                        # ====== Helper functions ======= #
                                        ###################################

def find_item(find_id, lst, id_name):
    """Helper function for filtering channel/message/dm"""
    return list(filter(lambda item: is_id(find_id, item, id_name), lst))

def is_id(find_id, item, id_name):
    """Check if item corresponds to id"""
    return item[id_name] == find_id

def check_pin_unpin(message, function):
    """
    Helper function to check if message is already pinned/unpinned
    If yes, raise error, else pin/unpin message
    """
    if function == "pin" and message["is_pinned"]:
        raise InputError(description="Message is already pinned")
    if function == "unpin" and not message["is_pinned"]:
        raise InputError(description="This message id is already unpinned.")
    message["is_pinned"] = True if function == "pin" else False
    
def check_user_pin_unpin_channel_msg(auth_user_id, message, channels, function):
    """Helper function to check if user can do function for the channel message"""
    # Locate channel
    valid_channel = find_item(message["channel_id"], channels, "id")[0]
    # If user not in channel, InputError
    if auth_user_id not in valid_channel['all_members']:
        raise InputError(description="This user is not a member of this channel.")
    # If user not in message and not an owner, AccessError
    elif auth_user_id not in valid_channel['owner_permissions']:
        raise AccessError(description=f"This user is not allowed to {function} this message.")

def check_user_pin_unpin_dm_msg(auth_user_id, message, dms, function):
    """Helper function to check if user can do function for the dm message"""
    # Locate DM
    valid_dm = find_item(message["dm_id"], dms, "dm_id")[0]
    # If user not in DM, InputError
    if auth_user_id not in valid_dm['members']:
        raise InputError(description="This user is not a member of this DM.")
    # If user not in DM and not an owner, AccessError
    elif auth_user_id is not valid_dm['owner_of_dm']:
        raise AccessError(description=f"This user is not allowed to {function} this DM message.")

def pin_unpin_message(auth_user_id, message_id, store, function):
    """Helper function to pin/unpin message"""
    # Locate message in channels
    valid_channel_msg = find_item(message_id, store["channel_messages"], "message_id")
    # Locate message in DMs
    valid_dm_msg = find_item(message_id, store["dm_messages"], "message_id")

    # If message in channel
    if valid_channel_msg:
        check_user_pin_unpin_channel_msg(auth_user_id, valid_channel_msg[0], store["channels"], function)
        check_pin_unpin(valid_channel_msg[0], function)
    elif valid_dm_msg:
        check_user_pin_unpin_dm_msg(auth_user_id, valid_dm_msg[0], store["dms"], function)
        check_pin_unpin(valid_dm_msg[0], function)
    else:
        # If message not found, InputError
        raise InputError(description="This message id is not valid.")

def check_user_edit_remove_channel_msg(auth_user_id, message, channels, function):
    """Helper function to check if user can do function for the channel message"""
    # There must be a channel that contains this message if message_id is valid
    valid_channel = find_item(message["channel_id"], channels, "id")[0]
    # Check auth user id is in channel
    if auth_user_id not in valid_channel["all_members"]:
        raise InputError(description="This user is not a member of this channel.")
    # Check auth user id is the message sender or a channel owner
    if auth_user_id != message["u_id"] and auth_user_id not in valid_channel["owner_permissions"]:
        raise AccessError(description=f"This user is not allowed to {function} this message.")
    
def check_user_edit_remove_dm_msg(auth_user_id, message, dms, function):
    """Helper function to check if user can do function for the dm message"""
    # There must be a dm that contains this message if message_id is valid
    valid_dm = find_item(message["dm_id"], dms, "dm_id")[0]
    # Check auth user id is in dm
    if auth_user_id not in valid_dm["members"]:
        raise InputError(description="This user is not a member of this DM.")
    # Check auth user id is the message sender or owner of dm
    if auth_user_id != message["u_id"] and auth_user_id != valid_dm["owner_of_dm"]:
        raise AccessError(description=f"This user is not allowed to {function} this message.")

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

def edit_remove_msg(auth_user_id, message_id, store, function, message):
    """Helper function to edit/remove message"""
    # Locate message in channel messages
    valid_channel_msg = find_item(message_id, store["channel_messages"], "message_id")
    # Locate message in dm messages
    valid_dm_msg = find_item(message_id, store["dm_messages"], "message_id")
    # Message belongs to a channel
    if valid_channel_msg:
        check_user_edit_remove_channel_msg(auth_user_id, valid_channel_msg[0], store["channels"], function)
        update_message(message, store["channel_messages"], valid_channel_msg[0])
    # Message belongs to a DM
    elif valid_dm_msg:
        check_user_edit_remove_dm_msg(auth_user_id, valid_dm_msg[0], store["dms"], function)
        update_message(message, store["dm_messages"], valid_dm_msg[0])
    else:
        raise InputError("Invalid message id")

def get_message(message_id, channel_messages, dm_messages):
    """Helper function to get message"""
    # Find channel/dm of og message
    channel_msg = find_item(message_id, channel_messages, "message_id")
    dm_msg = find_item(message_id, dm_messages, "message_id")
    return (channel_msg, dm_msg)

def react_message(message, reaction):
    """Helper function to create/append new reaction"""
    # Find any existing react ids of message
    react = find_item(reaction[1], message["reacts"], "react_id")
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

def sendlater(auth_user_id, message_id, message, time_sent, message_type, group_id, group_id_name):
    """Threading function to send message when designated time is reached"""
    store = data_store.get()
    new_message = {
        "message_id": message_id,
        "u_id": auth_user_id,
        group_id_name: group_id,
        'message': message,
        'time_created': time_sent,   
        'reacts': [],
        'is_pinned': False,
    }
    store[message_type].append(new_message)
    users_stats_v1()
    data_store.set(store)
    save()

def message_sendlater(auth_user_id, group_id, message, time_sent, group):
    """Helper function to send messages later"""
    store = data_store.get()
    time_now = time.time()
    time_difference = int(time_sent - time_now)
    # Switch id name between channel and dm
    id_name = "id" if group == CHANNEL else "dm_id"
    # Locate the channel/dm
    valid_group = find_item(group_id, store["channels" if group == CHANNEL else "dms"], id_name)
    group_name = "channel" if group == CHANNEL else "DM"
    # Check if valid dm id
    if not valid_group:
        raise InputError(description=f"Given {group_name} doesn't exist")
    # Check if user is part of dm
    if auth_user_id not in valid_group[0]["all_members" if group == CHANNEL else "members"]:
        raise AccessError(description=f"User is not apart of the {group_name}")
    # Check valid message length
    if len(message) > 1000:
        raise InputError(description="Message is too long")
    # Check if time_send is a time in the past
    if time_difference < 0:
        raise InputError(description="Time set is in the past")
    # Change id name for messages
    id_name = "channel_id" if group == CHANNEL else "dm_id"
    store['message_id_gen'] += 1
    # Depending whether its sendlater or sendlaterdm, need to switch between the message types
    message_type = "channel_messages" if group == CHANNEL else "dm_messages"
    arguments = [auth_user_id, store['message_id_gen'], message, time_sent, message_type, group_id, id_name]
    thread = threading.Timer(time_difference, sendlater, arguments)
    thread.start()

    data_store.set(store)
    return {
        "message_id": store['message_id_gen']
    }

def send_message(auth_user_id, group_id, message, group):
    """Helper function to send a message from channel or dm"""
    # Get variables from store
    store = data_store.get()
    group_name = "channel" if group == CHANNEL else "dm"
    group_messages = store[f"{group_name}_messages"]

    # Locate DM/Channel
    valid_group = find_item(group_id, store[f"{group_name}s"], "id" if group == CHANNEL else "dm_id")

    # If channel/dm not found, InputError
    if not valid_group:
        raise InputError(description=f"This {group_name} is not valid.")
    
    # If user not in channel/dm, InputError
    if auth_user_id not in valid_group[0]["all_members" if group == CHANNEL else "members"]:
        raise AccessError(description=f"This user is not a member of this {group_name}.")
    
    # Validates length of message
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="This message length is invalid.")

    # Increment message_id_gen
    store['message_id_gen'] += 1

    # Make up new message dictionary and append it in channel/dm_messages list
    new_message = {
        'message_id': store['message_id_gen'],
        'u_id': auth_user_id,
        f'{group_name}_id': group_id,
        'message': message,
        'time_created': int(time.time()),
        'reacts': [],
        'is_pinned': False,
    }
    group_messages.append(new_message)
    
    # Store data into data_store and return dictionary with the message_id
    data_store.set(store)
    return {
        'message_id': new_message['message_id']
    }
                                        #################################
                                        # ====== Main functions ======= #
                                        #################################

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
    return send_message(auth_user_id, channel_id, message, CHANNEL)

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
    return send_message(auth_user_id, dm_id, message, DM)

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
    edit_remove_msg(auth_user_id, message_id, store, "edit", message)
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
    store = data_store.get()
    edit_remove_msg(auth_user_id, message_id, store, "remove", "")
    # Store data into data_store and return empty dictionary
    data_store.set(store)
    return {}

def message_pin_v1(auth_user_id, message_id):
    """
    Given a message within a channel or DM, mark it as "pinned".

    Arguments: 
        auth_user_id (integer) - id of user pinning the message
        message_id (integer) - id of the message is being pinned

    Exceptions:
        InputError - Occurs when any of:
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
    pin_unpin_message(auth_user_id, message_id, store, "pin")
    # Store data into data_store and return empty dictionary
    data_store.set(store)
    return {}

def message_unpin_v1(auth_user_id, message_id):
    """
    Given a message within a channel or DM, remove its mark as pinned.

    Arguments: 
        auth_user_id (integer) - id of user unpinning the message
        message_id (integer) - id of the message is being unpinned

    Exceptions:
        InputError - Occurs when any of:
                        - message_id is not a valid message within a channel or 
                          DM that the authorised user has joined
                        - the message is not already pinned
        AccessError - Occurs when:
                        - message_id refers to a valid message in a joined 
                          channel/DM and the authorised user does not have 
                          owner permissions in the channel/DM.

    Return Value:
        Returns an empty dictionary

    """
    # Get variables from store
    store = data_store.get()
    pin_unpin_message(auth_user_id, message_id, store, "unpin")
    # Store data into data_store and return empty dictionary
    data_store.set(store)
    return {}

def message_sendlaterdm_v1(auth_user_id, dm_id, message, time_sent):
    return message_sendlater(auth_user_id, dm_id, message, time_sent, DM)
    
def message_sendlater_v1(auth_user_id, channel_id, message, time_sent):
    return message_sendlater(auth_user_id, channel_id, message, time_sent, CHANNEL)

def message_share_v1(auth_user_id, og_message_id, message, channel_id, dm_id):
    store = data_store.get()
    channel_messages = store["channel_messages"]
    dm_messages = store["dm_messages"]
    # Locate channel/dm
    valid_channel = find_item(channel_id, store["channels"], "id")
    valid_dm = find_item(dm_id, store["dms"], "dm_id")
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
        # Find which channel the og channel message belongs to (Channels cannot be deleted so can always find one)
        channel_og_message = find_item(valid_og_message["channel_id"], store["channels"], "id")[0]
        if auth_user_id not in channel_og_message["all_members"]:
            raise InputError(description="Message ID does not refer to a valid message within a channel/dm user has joined")
    else:
        # Find which DM the og dm message belongs to (Deleting DMs also deletes its messages, so if message is still valid, dm is still valid)
        dm_og_message = find_item(valid_og_message["dm_id"], store["dms"], "dm_id")[0]
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
    dm_msg = find_item(message_id, store["dm_messages"], "message_id")
    channel_msg = find_item(message_id, store["channel_messages"], "message_id")

    if react_id != 1:
        raise InputError("Invalid react ID")
    
    if channel_msg:
        # If channel message is valid then channel must be valid
        channel = find_item(channel_msg[0]["channel_id"], store["channels"], "id")[0]
        # Check if message id refers to a channel message such that user has joined that channel
        if auth_user_id not in channel["all_members"]:
            raise InputError("Not Authorised User")
        react_message(channel_msg[0], reaction)
    elif dm_msg:
        # If dm_message is valid then dm must be valid
        dm = find_item(dm_msg[0]["dm_id"], store["dms"], "dm_id")[0]
        # Check if message id refers to a dm message such that user has joined that dm
        if auth_user_id not in dm["members"]:
            raise InputError("Not Authorised User")
        react_message(dm_msg[0], reaction)
    else:
        raise InputError("Not a valid message ID")
            
    return {}
