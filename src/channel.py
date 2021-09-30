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
    # Checks if channel and start are valid inputs
    channel_valid = False
    start_valid = False
    selected_channel = {}
    store = data_store.get()
    channels = store['channels']

    # Scans if the channel exists
    for channel in channels:
        if channel['id'] == channel_id:
            channel_valid = True
            # Checks if the start value is valid within the length of 
            # messages in the channel.
            if start <= len(channel['messages']):
                start_valid = True
                selected_channel = channel  # Channel is also selected

    # If the channel_id or start value are invalid, then errors are raised.
    if channel_valid is False:
        raise InputError("This channel is not valid.")
    if start_valid is False:
        raise InputError("This start is not valid.")
    
    # Checks if the authorised user is a member of the channel
    member_valid = False
    for member in selected_channel['all_members']:
        if member == auth_user_id:
            member_valid = True

    # If the user is not a member, then an error is raised.
    if member_valid is False:
        raise AccessError('User is not authorised.')

    # The channel is scanned for its messages.
    index = start
    counter = 0
    channel_messages = selected_channel['messages']
    selected_messages = []
    while index < len(channel_messages) and counter <= 50:
        selected_messages.append(channel_messages[index])
        index += 1
        counter += 1

    # If the scanner hits the end of the messages, the end is -1
    # else, the end is the final message index.
    if counter != 51:
        end = -1
    else:
        end = index - 1

    # The selected messages, the start and the end values are returned.
    return {
        'messages': selected_messages,
        'start': start,
        'end': end,
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
