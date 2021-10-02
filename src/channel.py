"""
Various methods to interact with channels such as inviting users to the channel,
returning the details of the channel, joining channels and returning messages 
of the channel
"""

from src.error import InputError, AccessError
from src.data_store import data_store

def channel_invite_v1(auth_user_id, channel_id, u_id):
    store = data_store.get()
    users = store['users']
    channels = store['channels']

    #boolean operator
    valid_channel = 0
    valid_user = 0
    #checks for valid channel
    for channel in channels:
        if channel_id == channel['id']:
            valid_channel = 1
            #checks to see authorised member is sending channel invitation
            if auth_user_id not in channel['all_members']: 
                raise AccessError("not authorised user")
            break
    if valid_channel == 0:
        raise InputError("not valid channel ID")   
    #checks for valid user 
    for user in users:
        if u_id == user['id']:
            valid_user = 1
            break
    
    if valid_user == 0:
        raise InputError("not valid user")   
    #checks to see if member
    if u_id in channel['all_members']:
        raise InputError("already member")
   
    channel['all_members'].append(u_id)
    
    if user['permission'] == 1:
        channel['owner__permissions'].append(u_id)   
    
    data_store.set(store)
    
    return {}

def channel_details_v1(auth_user_id, channel_id):
    # Grabbing the items from the data_store.
    store = data_store.get()
    channels = store['channels']
    users = store['users']
    channel_details = {}

    # Checks if user exist
    check_valid_user(auth_user_id, users)
    
    channel_exists = 0
    owner_ids = None
    all_members_ids = None

    # Searches for a channel with the same ID and stores its information.
    # Also checks if a channel exists.
    for channel in channels:
        if channel["id"] == channel_id:
            channel_exists = 1
            channel_details["name"] = channel["name"]
            channel_details["is_public"] = channel["is_public"]
            channel_details["owner_members"] = []
            channel_details["all_members"] = []
            # channel["owner_members"] and channel["all_members"] are lists of user IDs.
            owner_ids = channel["owner_members"]
            all_members_ids = channel["all_members"]

    if not channel_exists:
        raise InputError("Channel does not exist") 
    
    # Finds a user's information based on their user IDs.
    for user_data in users:
        if user_data["id"] in owner_ids:
            # Assigns the necessary keys required from user_data.
            user_info = assign_user_info(user_data)
            # Stores the owners' information into channel_details["owner_members"].
            channel_details["owner_members"].append(user_info)
        if user_data["id"] in all_members_ids:
            user_info = assign_user_info(user_data)
            channel_details["all_members"].append(user_info)

    an_invited_member = 0
    members = channel_details["all_members"]

    # Checks if the user is apart of the channel.
    for member in members:
        if member["u_id"] == auth_user_id:
            an_invited_member = 1

    if not an_invited_member:
        raise AccessError("User is not a member of the channel")

    return channel_details

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
    while index < len(channel_messages) and counter < 50:
        selected_messages.append(channel_messages[index])
        index += 1
        counter += 1

    # If the scanner hits the end of the messages, the end is -1
    # else, the end is the final message index.
    if counter != 50 or index == len(channel_messages):
        end = -1
    else:
        end = index

    # The selected messages, the start and the end values are returned.
    return {
        'messages': selected_messages,
        'start': start,
        'end': end,
    }
    
def channel_join_v1(auth_user_id, channel_id):
    """
    Auth_user_id joins the channel by being appended to the channels
    members' list.

    Arguments:
    auth_user_id (<integer>) - id of the user joining the channel
    channel_id (<integer>) - id of the channel

    Exceptions:
    InputError - Occurs when given:
                    - channel_id does not exist/invalid
                    - auth_user_id is already a member of the channel
    AccessError - Occurs when given:
                    - auth_user_id does not exist/invalid
                    - channel_id corresponding to channel is private and 
                      the user is not a global owner or a member of the 
                      channel

    Return value:
        Returns an empty dictionary when user successfully joins the channel
    """
    
    store = data_store.get()
    users = store['users']
    channels = store['channels']

    # Check if user is valid
    user = check_valid_user(auth_user_id, users)
    
    # Check if channel is valid
    channel_exists = 0
    for channel in channels:
        if channel_id == channel['id']:
            channel_exists = 1
            break
        
    if not channel_exists:
        raise InputError("Invalid Channel ID")
    
    if auth_user_id in channel['all_members']:
        raise InputError("Already a member of channel")

    # Global members cannot join private channels
    if channel['is_public'] is False and user['permission'] == 2:
        raise AccessError("Channel is private")
    
    # Give channel owner permissions to global owners
    if user['permission'] == 1:
        channel['owner_permissions'].append(auth_user_id)
    
    channel['all_members'].append(auth_user_id)
    
    data_store.set(store)

    return {}


def assign_user_info(user_data_placeholder):
    """Assigns the user information with the appropriate key names required in the spec"""
    return {
        'u_id': user_data_placeholder['id'],
        'email': user_data_placeholder['email'],
        'name_first': user_data_placeholder['name_first'],
        'name_last': user_data_placeholder['name_last'],
        'handle_str':user_data_placeholder['handle']
    }

def check_valid_user(auth_user_id, users):
    """Helper function to check if user is valid"""
    user_exists = 0
    for user in users:
        if auth_user_id == user['id']:
            user_exists = 1
            break
    
    if not user_exists:
        raise AccessError("User is not authorised.")
    else:
        return user