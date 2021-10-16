from src.error import InputError, AccessError
from src.data_store import data_store
import time

def message_send_v1(auth_user_id, channel_id, message):
    store = data_store.get()
    channels = store["channels"]
    messages = store["messages"]

    selected_channel = {}
    valid_channel = False
    valid_member = False
    valid_message = False

    for channel in channels:
        if channel['id'] == channel_id:
            valid_channel = True
            selected_channel = channel
    
    if auth_user_id in selected_channel['all_members']:
        valid_member = True
    
    if len(message) > 0 and len(message) < 1001:
        valid_message = True

    if not valid_channel:
        raise InputError("This channel is not valid.")
    elif not valid_member:
        raise AccessError("This user is not a member of this channel.")
    elif not valid_message:
        if len(message) < 1:
            raise InputError("This message is too short.")
        else:
            raise InputError("This message is too long.")

    store['message_count'] += 1

    new_message = {
        'message_id': store['message_count'],
        'u_id': auth_user_id,
        'channel_id': channel_id,
        'message': message,
        'time_create': time.time(),
    }
    messages.append(new_message)
    data_store.set(store)


    store = data_store.get()
    return {
        'message_id': store['messages'][new_message['message_id']]
    }
