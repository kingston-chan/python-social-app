from src.data_store import data_store
from src.error import AccessError

store = data_store.get()
channels = store['channels']
users = store['users']

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
    user_exists = 0
    for user in users:
        if user['id'] == auth_user_id:
            user_exists = 1
    
    if not user_exists:
        raise AccessError("User does not exist")
    
    channels_dict = {}
    channels_dict['channel_id'] = []
    channels_dict['name'] = []

    for channel in channels:
        channels_dict['channel_id'].append(channel['id'])
        channels_dict['name'].append(channel['name'])

    return channels_dict

def channels_create_v1(auth_user_id, name, is_public):
    return {
        'channel_id': 1,
    }