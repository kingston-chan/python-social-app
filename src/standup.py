from src.data_store import data_store
from src.error import InputError, AccessError
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

    x = threading.timer(length, standup_thread_send_msg, args=(auth_user_id, channel_id))
    x.start()

    return {'time_finish': time_finish}

def standup_active_v1(auth_user_id, channel_id):
    store = data_store.get()
    channels = store['channels']

    status = False
    channel_exist = False

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

    return {'is_active': status, 'time_finish': time_finish}

def standup_send_v1():
    pass

def standup_thread_send_msg(auth_user_id, channel_id):
    pass