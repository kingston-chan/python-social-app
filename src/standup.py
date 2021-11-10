from src.data_store import data_store
from src.error import InputError, AccessError
from src.message import message_send_v1, find_item
from src.user import users_stats_v1, user_stats_v1
import time
import threading


def standup_start_v1(auth_user_id, channel_id, length):
    store = data_store.get()
    channels = store['channels']
    time_finish = time.time() + length
    
    valid_channel = find_item(channel_id, channels, "id")
    if not valid_channel:
        raise InputError(description="Channel doesn't exist")
    
    if auth_user_id not in valid_channel[0]['all_members']:
        raise AccessError(description="This user is not a member of this channel.")

    if length < 0:
        raise InputError(description="Length is a negative integer")
    
    if valid_channel[0]["standup"]["active"]:
        raise InputError(description="Standup already active")
    
    valid_channel[0]["standup"]["active"] = True
    valid_channel[0]["standup"]["auth_user_id"] = auth_user_id
    valid_channel[0]["standup"]["time_finish"] = time_finish

    x = threading.Timer(length, standup_thread_send_msg, args=(auth_user_id, channel_id))
    x.start()

    store['channels'] = channels
    data_store.set(store)

    return {'time_finish': int(time_finish)}

def standup_active_v1(auth_user_id, channel_id):
    
    store = data_store.get()
    channels = store['channels']

    try:
        channel_id = int(channel_id)
    except ValueError:
        raise InputError(description="Channel doesn't exist") from InputError
    
    valid_channel = find_item(channel_id, channels, "id")

    if not valid_channel:
        raise InputError(description="Channel doesn't exist")
    
    if auth_user_id not in valid_channel[0]['all_members']:
        raise AccessError(description="This user is not a member of this channel.")
    
    time_finish = valid_channel[0]["standup"]["time_finish"]
    
    data_store.set(store)

    return {
        'is_active': valid_channel[0]["standup"]["active"],
        'time_finish': int(time_finish) if time_finish else None 
    }

def standup_send_v1(auth_user_id, channel_id, message):
    store = data_store.get()
    channels = store['channels']
    users = store['users']

    user_handle = find_item(auth_user_id, users, "id")[0]["handle"]
    joined_msg = f"{user_handle}: {message}"
    
    valid_channel = find_item(channel_id, channels, "id")

    if not valid_channel:
        raise InputError(description="Channel doesn't exist")
    
    if auth_user_id not in valid_channel[0]['all_members']:
        raise AccessError(description="This user is not a member of this channel.")
    
    if not valid_channel[0]["standup"]["active"]:
        raise InputError(description="Standup is not running")
    
    if len(message) > 1000:
        raise InputError(description="Message is over 1000 characters")
    
    valid_channel[0]["standup_queue"].append(joined_msg)

    store['channels'] = channels
    data_store.set(store)
    return

def standup_thread_send_msg(auth_user_id, channel_id):
    store = data_store.get()
    channels = store['channels']
    users = store['users']
    store = data_store.get()
    for user in users:
        if auth_user_id == user["id"]:
            user["message_count"] += 1
            break

    for channel in channels:
        if channel["id"] == channel_id:
            message = "\n".join(channel["standup_queue"])
            channel["standup"]["active"] = False
            channel["standup"]["time_finish"] = None
            channel["standup_queue"] = []
            if not message:
                break
            message_send_v1(auth_user_id, channel_id, message)
            break
    store['users'] = users
    store['channels'] = channels
    data_store.set(store)
    users_stats_v1()
    user_stats_v1(auth_user_id)
    return
    
