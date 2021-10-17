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
        auth_user_id (integer) - id of user creating the channel
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
    store = data_store.get()
    channels = store["channels"]
    messages = store["channel_messages"]

    selected_channel = {}
    valid_channel = False
    valid_message = False

    for channel in channels:
        if channel['id'] == channel_id:
            valid_channel = True
            selected_channel = channel
    
    if len(message) > 0 and len(message) < 1001:
        valid_message = True

    if not valid_channel:
        raise InputError("This channel is not valid.")
    elif not valid_message:
        if len(message) < 1:
            raise InputError("This message is too short.")
        else:
            raise InputError("This message is too long.")

    if auth_user_id not in selected_channel['all_members']:
        raise AccessError("This user is not a member of this channel.")

    store['message_id_gen'] += 1

    new_message = {
        'message_id': store['message_id_gen'],
        'u_id': auth_user_id,
        'channel_id': channel_id,
        'message': message,
        'time_created': int(time.time()),
    }
    messages.append(new_message)
    data_store.set(store)
    store = data_store.get()
    return {
        'message_id': store['message_id_gen']
    }

def message_edit_v1(auth_user_id, message_id, message):
    """
    Given a message, update its text with new text. 
    If new text is blank, the message is deleted.

    Arguments: 
        auth_user_id (integer) - id of user creating the channel
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

    store = data_store.get()
    channels = store["channels"]
    messages = store["channel_messages"]

    selected_channel = {}
    valid_message_id = False
    valid_message = False

    for target_message in messages:
        if int(target_message['message_id']) == int(message_id):
            valid_message_id = True
            selected_message = target_message
    
    if len(message) < 1001:
        valid_message = True

    if not valid_message_id:
        raise InputError("This message id is not valid.")
    elif not valid_message:
        raise InputError("This message is too long.")

    for channel in channels:
        if int(channel['id']) == int(selected_message['channel_id']):
            selected_channel = channel

    if auth_user_id not in selected_channel['all_members']:
        raise AccessError("This user is not a member of this channel.")
    elif auth_user_id is not selected_message['u_id']:
        if auth_user_id not in selected_channel['owner_members'] and auth_user_id not in selected_channel['owner_permissions']:
            raise AccessError("This user is not allowed to edit this message.")

    if message == "":
        messages.remove(selected_message)
    else:
        selected_message['message'] = message

    data_store.set(store)
    store = data_store.get()
    return {}