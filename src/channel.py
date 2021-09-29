from src.error import InputError, AccessError
from src.data_store import data_store

def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    
    store = data_store.get()
    users = store['users']
    channels = store['channels']
    
    checklist = []
    for user in users:
        if auth_user_id == user['id']:
            checklist.append(1)
        else:
            checklist.append(0)
    if 1 not in checklist:
        raise InputError("Invalid user")

    checklist.clear()
    
    for channel in channels:
        if channel_id == channel['id']:
            checklist.append(1)
        else:
            checklist.append(0)
        
    if 1 not in checklist:
        raise AccessError("Invalid Channel ID")
        
    checklist.clear()
    
    for channel in channels:
        if channel_id == channel['id']:
            if auth_user_id in channel['all_members']:
                raise InputError("Already a member of channel")
        
            if channel['is_public'] != True:
                raise AccessError("Channel is private")
                
    for channel in channels:
        if channel_id == channel['id']: 
            channel['all_members'].append(auth_user_id)

    data_store.set(store)
        
    checklist.clear()        
    return {}
