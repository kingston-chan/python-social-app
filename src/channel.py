from src.data_store import data_store
from src.error import InputError, AccessError

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
    # checks if channel and start are valid inputs
    channel_valid = False
    start_valid = False
    selected_channel = {}
    store = data_store.get()
    channels = store['channels']
    for channel in channels:
        if channel["channel_id"] == channel_id:
            channel_valid = True
            if start <= len(channel["messages"]):
                start_valid = True
                selected_channel = channel

    if channel_valid is False:
        raise InputError("This channel is not valid.")
    if start_valid is False:
        raise InputError("This start is not valid.")
    
    member_valid = False
    for member in selected_channel[all_members]:
        if member["u_id"] == auth_user_id:
            member_valid = True
    
    if member_valid is False:
        raise AccessError("User is not authorised.")

    index = start
    counter = 0
    messages = selected_channel[messages]
    selected_messages = []
    while index <= len(messages) and counter < 50:
        for message in messages:
            if message["message_id"] == index:
                selected_messages.append(message)
        index += 1
        counter += 1

    if counter != 50:
        end = -1
    else:
        end = index

    return {
        'messages': selected_messages,
        'start': start,
        'end': end,
    }
def channel_join_v1(auth_user_id, channel_id):
    return {
    }
