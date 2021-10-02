"""
Functions to:
- Create a channel
- List all channels of user is in
- List all channels
"""

from src.error import InputError, AccessError
from src.data_store import data_store

def user_exists(auth_user_id, users):
    """Helper function to verify user"""
    user_exist = False
    for user in users:
        if user['id'] == auth_user_id:
            user_exist = True

    if not user_exist:
        raise AccessError("User does not exist")

def channels_list_v1(auth_user_id):
    """
    List all channels that the user is a member of
    
    Arguments:
        auth_user_id (integer) - id of user to list channels they are a member of

    Exceptions:
        InputError - does not occur in this function
        AccessError - occurs when given auth_user_id is invalid

    Return Value:
        Returns a dictionary containing 'channels' which is a list of channels
        containing the id and name of the channel the auth_user_id is a member of 
        given that the auth_user_id is valid.

    """
    store = data_store.get()
    users = store['users']
    channels = store['channels']

    # Check if auth_user_id is valid
    user_exists(auth_user_id, users)

    channels_list = []
    # Append all the channels the user is part of, that being a member or an owner
    for channel in channels:
        if auth_user_id in channel['all_members']:
            channels_list.append({
                'channel_id': channel['id'],
                'name': channel['name']
            })

    return {
        'channels': channels_list
    }

def channels_listall_v1(auth_user_id):
    """
    List all channels created, given a valid user id 
    
    Arguments:
        auth_user_id (integer) - ID of the user requesting to list all channels.
    
    Exceptions:
        InputError - Does not occur in this function
        AccessError - Occurs when the user doesn't exist.
    
    Return Value:
        Returns a list of dictionaries containing:
            - channel_id (integer)
            - name (string)
    """
    # Grabs the items in the data_store
    store = data_store.get()
    channels = store['channels']
    users = store['users']
    # Checks if the user exists
    user_exists(auth_user_id, users)
    # Loops through 'channels' and appends a dictionary with 'channel_id' and
    # 'name' to a list.
    channels_list = []
    for channel in channels:
        channels_list.append({
            "channel_id": channel["id"],
            "name": channel["name"]
        })

    return {
        "channels": channels_list
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
        AccessError - Occurs when auth_user_id is invalid

    Return Value:
        Return a dictionary containing the channel id on successful 
        creation of channel
                        
    """
    store = data_store.get()
    users = store['users']
    channels = store['channels']

    # Check if user exists
    user_exists(auth_user_id, users)

    # Trim any leading/trailing whitespace characters in name
    name = name.strip()
    # Checks if the length of the name is valid
    if len(name) > 20 or len(name) < 1:
        raise InputError("Invalid channel name length")
    # Checks if given name is the same as an existing channel
    for channel in channels:
        if channel['name'].lower() == name.lower():
            raise InputError("Channel name already exists")
    # Create new channel with given information
    new_channel = {
        'name': name,
        'id': len(channels) + 1,
        'owner_members': [],
        'owner_permissions': [],
        'all_members': [],
        'is_public': is_public,
        'messages': [],
    }

    # Add the creator of the channel to the list
    # of owner_members and all_members
    new_channel['owner_members'].append(auth_user_id)
    new_channel['owner_permissions'].append(auth_user_id)
    new_channel['all_members'].append(auth_user_id)
    channels.append(new_channel)
    data_store.set(store)
    return {
        'channel_id': new_channel['id']
    }
