from types import MemberDescriptorType
from src.data_store import data_store
from src.error import AccessError
from src.error import InputError


def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    store = data_store.get()
    channels = store['channels']
    users = store['users']
    channel_details = {}

    user_exists = 0
    for user in users:
        if user['id'] == auth_user_id:
            user_exists = 1
    
    if not user_exists:
        raise AccessError("User does not exist")
    
    channel_exists = 0
    owner_id = None
    all_members_id = None
    for channel in channels:
        if channel["id"] == channel_id:
            channel_exists = 1
            channel_details["name"] = channel["name"]
            channel_details["is_public"] = channel["is_public"]
            channel_details["owner_members"] = []
            channel_details["all_members"] = []
            owner_id = channel["owner_members"]
            all_members_id = channel["all_members"]

    if not channel_exists:
        raise InputError("Channel does not exist")
    
    
    for user_info in users:
        for owners in owner_id:
            if user_info["id"] == owners:
                # user_return_info = {}
                # user_return_info["email"] = user_info["email"]
                # user_return_info["name_first"] = user_info["name_first"]
                # user_return_info["name_last"] = user_info["name_last"]
                # user_return_info["handle"] = user_info["handle"]
                # user_return_info["id"] = user_info["id"]
                user_info_placeholder = user_info
                user_info_placeholder.pop("password", None)
                channel_details["owner_members"].append(user_info_placeholder)
        for all_members in all_members_id:
            if user_info["id"] == all_members:
                # user_return_info = {}
                # user_return_info["email"] = user_info["email"]
                # user_return_info["name_first"] = user_info["name_first"]
                # user_return_info["name_last"] = user_info["name_last"]
                # user_return_info["handle"] = user_info["handle"]
                # user_return_info["id"] = user_info["id"]
                user_info_placeholder = user_info
                user_info_placeholder.pop("password", None)
                channel_details["all_members"].append(user_info_placeholder)

    an_invited_member = 0

    members = channel_details["all_members"]
    for member in members:
        if member["id"] == auth_user_id:
            an_invited_member = 1

    if not an_invited_member:
        raise AccessError("User is not a member of the channel")
    
    print(channel_details)
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