from types import MemberDescriptorType
from src.data_store import data_store
from src.error import AccessError, InputError

def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    # Grabbing the items from the data_store.
    store = data_store.get()
    channels = store['channels']
    users = store['users']
    channel_details = {}

    # Checks if user exist
    user_exists = 0
    for user in users:
        if user['id'] == auth_user_id:
            user_exists = 1
    
    if not user_exists:
        raise AccessError("User does not exist")
    
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
    for user_info in users:
        if user_info["id"] in owner_ids:
            # Pops off "password" from user_info_placeholder as "password" isn't needed.
            user_info_placeholder = user_info
            user_info_placeholder.pop("password", None) 
            # Stores the owners' information into channel_details["owner_members"].
            channel_details["owner_members"].append(user_info_placeholder)
        if user_info["id"] in all_members_ids:
            user_info_placeholder = user_info
            user_info_placeholder.pop("password", None)
            channel_details["all_members"].append(user_info_placeholder)

    an_invited_member = 0
    members = channel_details["all_members"]

    # Checks if the user is apart of the channel.
    for member in members:
        if member["id"] == auth_user_id:
            an_invited_member = 1

    if not an_invited_member:
        raise AccessError("User is not a member of the channel")
    
    return channel_details

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
    return {
    }