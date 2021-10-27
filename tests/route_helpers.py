"""
Helper functions for route requests for testing
"""

import requests
from src.config import url

# ==== Auth ==== #

def auth_login(email, password):
    """
    Logins a user

    Arguments
        email (string)
        password (string)

    Return value
        Returns the response of the auth/login/v2 request which contains json { token, auth_user_id }
    """
    return requests.post(f"{url}/auth/login/v2", json={ "email": email, "password": password })

def auth_register(email, password, first_name, last_name):
    """
    Registers a user

    Arguments
        email (string)
        password (string)
        first_name (string)
        last_name (string)

    Return value
        Returns the response of the auth/register/v2 request which contains json { token, auth_user_id }
    """
    user_info = {
        "email": email, 
        "password": password, 
        "name_first": first_name, 
        "name_last": last_name
    }

    return requests.post(f"{url}/auth/register/v2", json=user_info)

def auth_logout(token):
    """
    Logs out a user

    Arguments
        token (JWT token)

    Return value
        Returns the response of the auth/logout/v1 request which contains json {}
    """

    return requests.post(f"{url}/auth/logout/v1", json={ "token": token })   

# ==== Channel ==== #

def channels_create(token, name, is_public):
    """
    Creates a new channel

    Arguments
        token (JWT token)
        name (string)
        is_public (boolean)

    Return value
        Returns the response of the channels/create/v2 request which contains json { channel_id }
    """
    channel_info = {
        "token": token, 
        "name": name, 
        "is_public": is_public
    }

    return requests.post(f"{url}/channels/create/v2", json=channel_info)

def channels_list(token):
    """
    Lists all channels the token's user is in

    Arguments
        token (JWT token)

    Return value
        Returns the response of the channels/list/v2 request which contains json { channels }
    """
    return requests.get(f"{url}/channels/list/v2", params={ "token": token })

def channels_listall(token):
    """
    Lists all channels

    Arguments
        token (JWT token)

    Return value
        Returns the response of the channels/listall/v2 request which contains json { channels }
    """
    return requests.get(f"{url}/channels/listall/v2", params={ "token": token })

def channel_details(token, channel_id):
    """
    Lists information about given channel 
    (name, is_public, owner_members, all_members)

    Arguments
        token (JWT token)
        channel_id (int)

    Return value
        Returns the response of the channel/details/v2 request which contains { name, is_public, 
        owner_members, all_members }
    """
    return requests.get(f"{url}/channel/details/v2", params={ "token": token, "channel_id": channel_id })

def channel_join(token, channel_id):
    """
    Given a channel_id of a channel that the authorised user can join, adds them to that channel.
    Authorised user is id in the token.

    Arguments
        token (JWT token)
        channel_id (int)

    Return value
        Returns the response of the channel/join/v2 request which contains json {}
    """
    return requests.post(f"{url}/channel/join/v2", json={ "token": token, "channel_id": channel_id })


def channel_invite(token, channel_id, u_id):
    """
    Invites a user with ID u_id to join a channel with ID channel_id. Once invited, the user is added to 
    the channel immediately. In both public and private channels, all members are able to invite users.

    Arguments
        token (JWT token)
        channel_id (int)
        u_id (int)

    Return value
        Returns the response of the channel/invite/v2 request which contains json {}
    """
    invite = {
        "token": token,
        "channel_id": channel_id,
        "u_id": u_id
    }
    return requests.post(f"{url}/channel/invite/v2", json=invite)

def channel_messages(token, channel_id, start):
    """
    Given a channel with ID channel_id that the authorised user is a member of, return up to 50 messages between 
    index "start" and "start + 50". Message with index 0 is the most recent message in the channel.
    This function returns a new index "end" which is the value of "start + 50", or, if this function has returned 
    the least recent messages in the channel, returns -1 in "end" to indicate there are no more messages to 
    load after this return.

    Arguments
        token (JWT token)
        channel_id (int)
        start (int)

    Return value
        Returns the response of the channel/messages/v2 request which contains json { messages, start, end }
    """
    info = { 
        "token": token, 
        "channel_id": channel_id, 
        "start": start 
    }
    return requests.get(f"{url}/channel/messages/v2", params=info)

def channel_leave(token, channel_id):
    """
    Given a channel with ID channel_id that the authorised user is a member of, remove them as a member 
    of the channel. Their messages should remain in the channel. If the only channel owner leaves, 
    the channel will remain.

    Arguments
        token (JWT token)
        channel_id (int)

    Return value
        Returns the response of the channel/leave/v2 request which contains json {}
    """
    info = { 
        "token": token, 
        "channel_id": channel_id, 
    }
    return requests.post(f"{url}/channel/leave/v1", json=info)

def channel_addowner(token, channel_id, u_id):
    """
    Make user with user id u_id an owner of the channel.

    Arguments
        token (JWT token)
        channel_id (int)
        u_id (int)

    Return value
        Returns the response of the channel/addowner/v1 request which contains json {}
    """
    info = { 
        "token": token, 
        "channel_id": channel_id,
        "u_id": u_id 
    }
    return requests.post(f"{url}/channel/addowner/v1", json=info)

def channel_removeowner(token, channel_id, u_id):
    """
    Remove user with user id u_id as an owner of the channel.

    Arguments
        token (JWT token)
        channel_id (int)
        u_id (int)

    Return value
        Returns the response of the channel/removeowner/v1 request which contains json {}
    """
    info = { 
        "token": token, 
        "channel_id": channel_id,
        "u_id": u_id 
    }
    return requests.post(f"{url}/channel/removeowner/v1", json=info)

# ==== Message ==== #

def message_send(token, channel_id, message):
    """
    Send a message from the authorised user to the channel specified by channel_id. 
    Note: Each message should have its own unique ID, i.e. no messages should share an 
    ID with another message, even if that other message is in a different channel.

    Arguments
        token (JWT token)
        channel_id (int)
        message (string)

    Return value
        Returns the response of the message/send/v1 request which contains json { message_id }
    """
    info = { 
        "token": token, 
        "channel_id": channel_id,
        "message": message 
    }
    return requests.post(f"{url}/message/send/v1", json=info)

def message_edit(token, message_id, message):
    """
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.

    Arguments
        token (JWT token)
        message_id (int)
        message (string)

    Return value
        Returns the response of the message/edit/v1 request which contains json {}
    """
    info = { 
        "token": token, 
        "message_id": message_id,
        "message": message 
    }
    return requests.put(f"{url}/message/edit/v1", json=info)

def message_remove(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments
        token (JWT token)
        message_id (int)

    Return value
        Returns the response of the message/remove/v1 request which contains json {}
    """
    info = { 
        "token": token, 
        "message_id": message_id
    }
    return requests.delete(f"{url}/message/remove/v1", json=info)

def message_senddm(token, dm_id, message):
    """
    Send a message from authorised_user to the DM specified by dm_id. Note: Each message should have 
    it's own unique ID, i.e. no messages should share an ID with another message, even if that other 
    message is in a different channel or DM.

    Arguments
        token (JWT token)
        dm_id (int)
        message (string)

    Return value
        Returns the response of the message/senddm/v1 request which contains { message_id }
    """
    info = {
        "token": token, 
        "dm_id": dm_id, 
        "message": message
    }
    return requests.post(f"{url}/message/senddm/v1", json=info)

def message_share(token, og_message_id, message, channel_id, dm_id):
    info = {
        "token": token,
        "og_message_id": og_message_id,
        "message": message,
        "channel_id": channel_id,
        "dm_id": dm_id
    }
    return requests.post(f"{url}/message/share/v1", json=info)

# ==== DM ==== #

def dm_create(token, u_ids):
    """
    u_ids contains the user(s) that this DM is directed to, and will not include the creator. 
    The creator is the owner of the DM. name should be automatically generated based on the 
    users that are in this DM. The name should be an alphabetically-sorted, comma-and-space-separated 
    list of user handles, e.g. 'ahandle1, bhandle2, chandle3'.

    Arguments
        token (JWT token)
        u_ids (list)

    Return value
        Returns the response of the dm/create/v1 request which contains json { dm_id }
    """
    return requests.post(f"{url}/dm/create/v1", json={ "token": token, "u_ids": u_ids })

def dm_list(token):
    """
    Returns the list of DMs that the user is a member of.
    User is the id in token

    Arguments
        token (JWT token)

    Return value
        Returns the response of the dm/list/v1 request which contains json { dms }
    """
    return requests.get(f"{url}/dm/list/v1", params={ "token": token })

def dm_remove(token, dm_id):
    """
    Remove an existing DM, so all members are no longer in the DM. This can only be 
    done by the original creator of the DM.

    Arguments
        token (JWT token)
        dm_id (int)

    Return value
        Returns the response of the dm/remove/v1 request which contains json {}
    """
    return requests.delete(f"{url}/dm/remove/v1", json={ "token": token, "dm_id": dm_id })

def dm_details(token, dm_id):
    """
    Given a DM with ID dm_id that the authorised user is a member of, provide basic details about the DM.

    Arguments
        token (JWT token)
        dm_id (int)

    Return value
        Returns the response of the dm/details/v1 request which contains json { name, members }
    """
    return requests.get(f"{url}/dm/details/v1", params={ "token": token, "dm_id": dm_id })

def dm_leave(token, dm_id):
    """
    Given a DM ID, the user is removed as a member of this DM. The creator is allowed to leave and 
    the DM will still exist if this happens. This does not update the name of the DM.

    Arguments
        token (JWT token)
        dm_id (int)

    Return value
        Returns the response of the dm/leave/v1 request which contains json {}
    """
    return requests.post(f"{url}/dm/leave/v1", json={ "token": token, "dm_id": dm_id })


def dm_messages(token, dm_id, start):
    """
    Given a DM with ID dm_id that the authorised user is a member of, return up to 50 messages between index "start" 
    and "start + 50". Message with index 0 is the most recent message in the DM. This function returns a new index 
    "end" which is the value of "start + 50", or, if this function has returned the least recent 
    messages in the DM, returns -1 in "end" to indicate there are no more messages to load after this return.

    Arguments
        token (JWT token)
        dm_id (int)
        start (int)

    Return value
        Returns the response of the dm/messages/v1 request which contains json { messages, start, end }
    """
    return requests.get(f"{url}/dm/messages/v1", params={ "token": token, "dm_id": dm_id, "start": start })

# ==== User ==== #

def users_all(token):
    """
    Returns a list of all users and their associated details.

    Arguments
        token (JWT token)

    Return value
        Returns the response of the users/all/v1 request which contains json { users }
    """
    return requests.get(f"{url}/users/all/v1", params={ "token": token })

def user_profile(token, u_id):
    """
    For a valid user, returns information about their user_id, email, first name, last name, and handle

    Arguments
        token (JWT token)
        u_id (int)

    Return value
        Returns the response of the user/profile/v1 request which contains json { user }
    """
    return requests.get(f"{url}/user/profile/v1", params={ "token": token, "u_id": u_id })

def user_profile_setname(token, name_first, name_last):
    """
    Update the authorised user's first and last name
    
    Arguments
        token (JWT token)
        name_first (string)
        name_last (string)

    Return value
        Returns the response of the user/profile/setname/v1 request which contains {}
    """
    info = {
        "token": token,
        "name_first": name_first,
        "name_last": name_last
    }
    return requests.put(f"{url}/user/profile/setname/v1", json=info)

def user_profile_setemail(token, email):
    """
    Update the authorised user's email address

    Arguments
        token (JWT token)
        email (string)

    Return value
        Returns the response of the user/profile/setemail/v1 request which contains json {}
    """
    return requests.put(f"{url}/user/profile/setemail/v1", json={ "token": token, "email": email })

def user_profile_sethandle(token, handle_str):
    """
    Update the authorised user's handle (i.e. display name)

    Arguments
        token (JWT token)
        handle_str (string)

    Return value
        Returns the response of the user/profile/sethandle/v1 request which contains json {}
    """
    return requests.put(f"{url}/user/profile/sethandle/v1", json={ "token": token, "handle_str": handle_str })

# ==== Admin ==== #

def admin_user_remove(token, u_id):
    """
    Given a user by their u_id, remove them from the Streams. This means they should be removed from all channels/DMs, 
    and will not be included in the list of users returned by users/all. Streams owners can remove other Streams owners 
    (including the original first owner). Once users are removed, the contents of the messages they sent will be replaced 
    by 'Removed user'. Their profile must still be retrievable with user/profile, however name_first should be 'Removed' 
    and name_last should be 'user'. The user's email and handle should be reusable.

    Arguments
        token (JWT token)
        u_id (int)

    Return value
        Returns the response of the admin/user/remove/v1 request which contains json {}
    """
    return requests.delete(f"{url}/admin/user/remove/v1", json={ "token": token, "u_id": u_id })

def admin_userpermission_change(token, u_id, permission_id):
    """
    Given a user by their user ID, set their permissions to new permissions described by permission_id.

    Arguments
        token (JWT token)
        u_id (int)
        permission_id (int)

    Return value
        Returns the response of the admin/user/remove/v1 request which contains json {}
    """
    info = {
        "token": token,
        "u_id": u_id,
        "permission_id": permission_id
    }
    return requests.post(f"{url}/admin/userpermission/change/v1", json=info)

def clear():
    """
    Clears the data store
    
    Arguments
        None

    Return value
        None
    """
    requests.delete(f"{url}/clear/v1")