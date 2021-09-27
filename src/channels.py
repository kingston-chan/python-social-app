from src.error import InputError, AccessError
from src.data_store import data_store


def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_listall_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_create_v1(auth_user_id, name, is_public):
    # Channel contains channel_name, owner_members, is_public, all_members, 
    # channel_id, messages
    store = data_store.get()
    users = store['users']
    channels = store['channels']

    # Check if user exists
    user_exists = 0
    for user in users:
        if user['id'] == auth_user_id:
            user_exists = 1

    if user_exists == 0:
        raise AccessError("User does not exist")

    # Checks if given name is the same as an existing channel
    for channel in channels:
        
        if channel['name'].lower() == name.lower():
            raise InputError("Channel name already exists")

    # Checks if the length of the name is valid
    if len(name) > 20 or len(name) < 1:
        raise InputError("Invalid channel name length")

    # Create new channel with given information
    new_channel = {
        'name': name,
        'id': len(channels) + 1,
        'owner_members': [],
        'all_members': [],
        'is_public': is_public,
        'messages': [],
    }

    new_channel['owner_members'].append(auth_user_id)
    new_channel['all_members'].append(auth_user_id)
    
    channels.append(new_channel)

    data_store.set(store)
    
    return {
        'channel_id': new_channel['id']
    }
