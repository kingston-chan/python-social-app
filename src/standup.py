from src.data_store import data_store
from src.error import InputError, AccessError
from src.message import message_send_v1
import time
import threading


def standup_start_v1(auth_user_id, channel_id, length):
    store = data_store.get()
    channels = store['channels']
    

    time_finish = time.time() + length


    channel_exist = False
    for channel in channels:
        if channel["id"] == channel_id:
            if channel["standup"]["active"] == True:
                raise InputError(description="Standup already active")

            channel["standup"]["active"] = True
            channel["standup"]["auth_user_id"] = auth_user_id
            channel["standup"]["time_finish"] = time_finish
            channel_exist = True
            break
    
    if auth_user_id not in channel['all_members']:
        raise AccessError(description="This user is not a member of this channel.")

    if not channel_exist:
        raise InputError(description="Channel doesn't exist")
    
    if length < 0:
        raise InputError(description="Length is a negative integer")

    x = threading.Timer(length, standup_thread_send_msg, args=(auth_user_id, channel_id))
    x.start()

    store['channels'] = channels
    data_store.set(store)

    return {'time_finish': time_finish}

def standup_active_v1(auth_user_id, channel_id):
    
    store = data_store.get()
    channels = store['channels']

    try:
        channel_id = int(channel_id)
    except ValueError:
        raise InputError(description="Channel doesn't exist") from InputError

        
    status = False
    channel_exist = False
    time_finish = None

    for channel in channels:
        if channel["id"] == channel_id:
            if channel["standup"]["active"] == True:
                status = True
                time_finish = channel["standup"]["time_finish"]
            
            channel_exist = True
            break

    if not channel_exist:
        raise InputError(description="Channel doesn't exist")
    
    if auth_user_id not in channel['all_members']:
        raise AccessError(description="This user is not a member of this channel.")
    
    store['channels'] = channels
    data_store.set(store)

    return {'is_active': status, 'time_finish': time_finish}

def standup_send_v1(auth_user_id, channel_id, message):
    store = data_store.get()
    channels = store['channels']
    users = store['users']

    if len(message) > 1000:
        raise InputError(description="Message is over 1000 characters")

    for user in users:
        if user["id"] == auth_user_id:
            joined_msg = str(user["handle"]) + ": " + str(message)


    channel_exist = False
    for channel in channels:
        if channel["id"] == channel_id:
            if auth_user_id not in channel['all_members']:
                raise AccessError(description="This user is not a member of this channel.")
            if channel["standup"]["active"] == False:
                raise InputError(description="Standup is not running")
        
            channel["standup_queue"].append(joined_msg)
            channel_exist = True
            break

    if not channel_exist:
        raise InputError(description="Channel doesn't exist")
    
    

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
            standup_queue = channel["standup_queue"]
            channel["standup_queue"] = []
            channel["standup"]["active"] = False
            message = "\n".join(item for item in standup_queue)
            message_send_v1(auth_user_id, channel_id, message)
            break
    store['users'] = users
    store['channels'] = channels
    data_store.set(store)

    return
    
