"""
Functions to:
- Create a channel
- List all channels of user is in
- List all channels
"""

from src.error import InputError, AccessError
from src.data_store import data_store

def channel_output(channel):
    return {
        "channel_id": channel["id"],
        "name": channel["name"]
    }

def channels_list_v1(auth_user_id):
    """
    List all channels that the user is a member of
    
    Arguments:
        auth_user_id (integer) - id of user to list channels they are a member of

    Exceptions:
        InputError - does not occur in this function

    Return Value:
        Returns a dictionary containing 'channels' which is a list of channels
        containing the id and name of the channel the auth_user_id is a member of 
        given that the auth_user_id is valid.

    """
    store = data_store.get()
    channels = store['channels']

    # Append all the channels the user is part of, that being a member or an owner
    channels_list = filter(lambda channel: auth_user_id in channel["all_members"], channels)

    return {
        'channels': list(map(channel_output, channels_list))
    }

def channels_listall_v1(auth_user_id):
    """
    List all channels created, given a valid user id 
    
    Arguments:
        auth_user_id (integer) - ID of the user requesting to list all channels.
    
    Exceptions:
        InputError - Does not occur in this function
    
    Return Value:
        Returns a list of dictionaries containing:
            - channel_id (integer)
            - name (string)
    """
    # Grabs the items in the data_store
    store = data_store.get()
    # Loops through 'channels' and appends a dictionary with 'channel_id' and
    # 'name' to a list.
    return {
        "channels": list(map(channel_output, store["channels"]))
    }

def channels_create_v1(auth_user_id, name, is_public):
    """
    Create a new channel, given a valid user id

    Arguments: 
        auth_user_id (integer) - id of user creating the channel
        name (string) - chosen name of channel being created
        is_public(boolean) - either private or public channel

    Exceptions:
        InputError - Occurs when given:
                        - name for channel is not between 1 and 20
                          characters inclusive
                        - channel name already exists (case sensitive)

    Return Value:
        Return a dictionary containing the channel id on successful 
        creation of channel
                        
    """
    store = data_store.get()
    # Trim any leading/trailing whitespace characters in name
    name = name.strip()
    # Checks if the length of the name is valid
    if len(name) > 20 or len(name) < 1:
        raise InputError(description="Invalid channel name length")
    # Checks if given name is the same as an existing channel
    if [channel for channel in store['channels'] if channel['name'].lower() == name.lower()]:
        raise InputError(description="Channel name already exists")
    # Create new channel with given information
    new_channel = {
        'name': name,
        'id': len(store['channels']) + 1,
        # Add the creator of the channel to the list
        # of owner_members and all_members
        'owner_members': [auth_user_id],
        'owner_permissions': [auth_user_id],
        'all_members': [auth_user_id],
        'ban_list': [],
        'is_public': is_public,
        'standup': {'active': False, 'auth_user_id': None, 'time_finish': None},
        'standup_queue': [],
        'wordbomb': {'active': False, 'user_turn': None, 'turn_count': 0, 'bomb_str': None, 'lives':{}}
    }

    store['channels'].append(new_channel)
    data_store.set(store)
    return {
        'channel_id': new_channel['id']
    }
