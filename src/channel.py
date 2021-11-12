"""
Various methods to interact with channels such as inviting users to the channel,
returning the details of the channel, joining channels, returning messages 
of the channel, leaving the channel and adding/removing owners
"""

from src.error import InputError, AccessError
from src.data_store import data_store
from src.notifications import store_notif

def assign_user_info(user_data_placeholder):
    """Assigns the user information with the appropriate key names required in the spec"""
    return {
        'u_id': user_data_placeholder['id'],
        'email': user_data_placeholder['email'],
        'name_first': user_data_placeholder['name_first'],
        'name_last': user_data_placeholder['name_last'],
        'handle_str':user_data_placeholder['handle'],
        'profile_img_url': user_data_placeholder['profile_img_url']
    }

def check_user_reacted(react, user_id):
    """Helper function for correctly mapping if user has reacted to message"""
    react["is_this_user_reacted"] = user_id in react["u_ids"]
    return react

def output_message(message, user_id):
    return {
        "message_id": message["message_id"],
        "u_id": message["u_id"],
        "message": message["message"],
        "time_created": message["time_created"],
        "reacts": list(map(lambda react: check_user_reacted(react, user_id), message["reacts"])),
        "is_pinned": message["is_pinned"]
    }

def channel_invite_v1(auth_user_id, channel_id, u_id):
    """
    Members of the channel can invite non-member users into their channel.

    Arguments: 
        auth_user_id (integer) - ID of the member of the channel
        channel_id (integer) - ID of the channel
        u_id (integer) - ID of the user being invited

    Exceptions:
        InputError - Occurs when given:
                        - channel_id is not valid
                        - u_id is not valid/is not a registered user
                        - user (u_id) being invited is already a member of 
                          the channel

        AccessError - Occurs when given:
                        - auth_user_id corresponding to the user is not a 
                          member of the given channel
        
    Return Value:
        Returns an empty dictionary on successfully inviting and adding user
        into the channel
    
    """
    store = data_store.get()
    users = store['users']
    channels = store['channels']

    valid_channel = list(filter(lambda channel: channel_id == channel['id'], channels))
    if not valid_channel:
        raise InputError(description="not valid channel ID")
    if auth_user_id not in valid_channel[0]['all_members']: 
        raise AccessError(description="not authorised user") 
    #checks for valid user 
    valid_user = list(filter(lambda user: u_id == user['id'] and user["email"] is not None and user["handle"] is not None, users))
    if not valid_user:
        raise InputError(description="not valid user")
    #checks to see if member
    if u_id in valid_channel[0]['all_members']:
        raise InputError(description="already member")
   
    valid_channel[0]['all_members'].append(u_id)
    
    if valid_user[0]['permission'] == 1:
        valid_channel[0]['owner_permissions'].append(u_id)
    
    # Find channel name and inviter handle
    user_inviting = list(filter(lambda user : auth_user_id == user["id"], store["users"]))
    channel = list(filter(lambda user: channel_id == user["id"], store["channels"]))

    # Create notification format
    notif_string = "{} added you to {}".format(user_inviting[0]["handle"],channel[0]["name"])
    notification = {"channel_id" : channel_id, "dm_id": -1, "notification_message": notif_string}
    
    store_notif(u_id, notification)
    
    data_store.set(store)
    
    return {}

def channel_details_v1(auth_user_id, channel_id):
    """
    If the authorised user is a member of the channel with 'channel_id', 
    provide basic details about the channel.

    Arguments:
        auth_user_id (integer) - ID of the user requesting for channel details.
        channel_id (integer) - ID of the channel requested for channel details.
    
    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel.
        AccessError - Occurs when channel_id is valid but the authorised user is
        not a member of the channel.
    
    Return Value:
        Returns 'channel_details', 
        a dictionary containing the following information about the channel:
            - name (string)
            - is_public (boolean)
            - owner_members (list of dictionaries)
            - all_members (list of dictionaries)
        Both list of dictionaries contain the following:
            - u_id (integer)
            - email (string)
            - name_first (string)
            - name_last (string)
            - handle_str (string)
    """
    # Grabbing the items from the data_store.
    store = data_store.get()
    channels = store['channels']
    users = store['users']
    
    # Find the channel requested
    valid_channel = list(filter(lambda channel: channel["id"] == channel_id, channels))
    if not valid_channel:
        raise InputError(description="Channel does not exist") 
    
    # Find channel owners and members information
    channel_owners = list(filter(lambda user: user["id"] in valid_channel[0]["owner_members"], users))
    channel_members = list(filter(lambda user: user["id"] in valid_channel[0]["all_members"], users))

    # Checks if the user is apart of the channel.
    if not list(filter(lambda member: member["id"] == auth_user_id, channel_members)):
        raise AccessError(description="User is not a member of the channel")

    return {
        "name": valid_channel[0]["name"],
        "is_public": valid_channel[0]["is_public"],
        # Stores the owners' information 
        "owner_members": list(map(assign_user_info, channel_owners)),
        # Assigns the necessary keys required from user_data.
        "all_members": list(map(assign_user_info, channel_members))
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    """
    Given a channel with ID channel_id that the authorised user is a member of, 
    return up to 50 messages between index "start" and "start + 50".

    Arguments: 
        auth_user_id (integer) - ID of the member of the channel
        channel_id (integer) - ID of the channel
        start (integer) - The index number of the first message to be returned.

    Exceptions:
        InputError - Occurs when given:
                        - channel_id does not refer to a valid channel
                        - start is greater than the total number of 
                          messages in the channel

        AccessError - Occurs when given:
                        - channel_id is valid and the authorised user is not 
                          a member of the channel
        
    Return Values:
        Returns a dictionary of a list of messages from index["start"] to
        index["start+50"], the start value and the end value.
    
    """
    # Checks if channel and start are valid inputs.
    store = data_store.get()
    channels = store['channels']
    channel_messages = store['channel_messages']

    # Scans if the channel exists.
    valid_channel = list(filter(lambda channel: channel['id'] == channel_id, channels))
    # If the channel_id or start value are invalid, then errors are raised.
    if not valid_channel:
        raise InputError(description="This channel is not valid.")

    # Checks if the start value is valid within the length of messages in the channel.
    valid_msgs = list(filter(lambda message: (message['channel_id'] == channel_id), channel_messages))
    
    # Find the length of the channel messages
    if start > len(valid_msgs):
        raise InputError(description="This start is not valid.")

    # If the user is not a member, then an error is raised.
    if auth_user_id not in valid_channel[0]["all_members"]:
        raise AccessError(description='User is not authorised.')

    # Most recent message is stored as the last element
    valid_msgs.reverse()
    output_msgs = valid_msgs[start:start+50] if len(valid_msgs) >= start + 50 else valid_msgs[start:]

    # The selected messages, the start and the end values are returned.
    return {
        'messages': list(map(lambda message: output_message(message, auth_user_id), output_msgs)),
        'start': start,
        # If the scanner hits the end of the messages, the end is -1
        # else, the end is the final message index.
        'end': start + 50 if start + 50 < len(valid_msgs) else -1,
    }
    
def channel_join_v1(auth_user_id, channel_id):
    """
    Auth_user_id joins the channel by being appended to the channels
    members' list.

    Arguments:
    auth_user_id (integer) - id of the user joining the channel
    channel_id (integer) - id of the channel

    Exceptions:
    InputError - Occurs when given:
                    - channel_id does not exist/invalid
                    - auth_user_id is already a member of the channel
    AccessError - Occurs when given:
                    - channel_id corresponding to channel is private and 
                      the user is not a global owner or a member of the 
                      channel

    Return value:
        Returns an empty dictionary when user successfully joins the channel
    """
    
    store = data_store.get()
    users = store['users']
    channels = store['channels']

    valid_user = list(filter((lambda user: user["id"] == auth_user_id), users))[0]
    valid_channel = list(filter(lambda channel: channel_id == channel['id'], channels))

    # Check if channel is valid
    if not valid_channel:
        raise InputError(description="Invalid Channel ID")
    
    if auth_user_id in valid_channel[0]['all_members']:
        raise InputError(description="Already a member of channel")

    # Global members cannot join private channels
    if valid_channel[0]['is_public'] is False and valid_user['permission'] == 2:
        raise AccessError(description="Channel is private")
    
    # Give channel owner permissions to global owners
    if valid_user['permission'] == 1:
        valid_channel[0]['owner_permissions'].append(auth_user_id)
    
    valid_channel[0]['all_members'].append(auth_user_id)
    
    data_store.set(store)

    return {}

def channel_addowner_v1(auth_user_id, channel_id, u_id):
    """
    Make user with user u_id the owner of the channel.

    Arguments:
        auth_user_id (integer) - ID of the authorised user promoting.
        channel_id (integer) - ID of the channel requested for channel_addowner.
        u_id (integer) - ID of the user being promoted.
    
    Exceptions:
        InputError - Occurs when:
                        - channel_id does not refer to a valid channel.
                        - u_id does not refer to a valid user
                        - u_id refers to a user who is not a member of the channel
                        - u_id refers to a user who is already an owner of the channel
        AccessError - Occurs when:
                        - channel_id is valid but the authorised user does not
                        have owner permissions for the channel.
    
    Return Value:
        Returns an empty dictionary on success.
    """
    store = data_store.get()
    users = store['users']
    channels = store['channels']


    # Searches for a channel with the same ID and stores its information.
    # Also checks if a channel exists.
    valid_channel = list(filter(lambda channel: channel["id"] == channel_id, channels))

    if not valid_channel:
        raise InputError(description="Channel does not exist") 
    
    if auth_user_id not in valid_channel[0]["owner_permissions"]:
        raise AccessError(description="User is not an owner/does not have the owner permissions.")
    
    # Checks if a user exists.
    if not list(filter(lambda user: u_id == user['id'], users)):
        raise InputError(description="Invalid user.")

    # Check if user being added as owner is in channel
    if u_id not in valid_channel[0]["all_members"]:
        raise InputError(description="User is not a member of the channel")

    # Check if user is not alreayd an owner
    if u_id in valid_channel[0]["owner_members"]:
        raise InputError(description="User is already an owner of the channel")

    # Assigns the new owner's u_id to the owner_members list and the owner_permissions list.
    valid_channel[0]["owner_members"].append(u_id)

    # Checks if they're a global owner.
    if u_id not in valid_channel[0]["owner_permissions"]:
        valid_channel[0]["owner_permissions"].append(u_id)

    data_store.set(store)

    return {}

def channel_leave_v1(auth_user_id, channel_id):
    """
    Auth_user_id leaves the channel by being removed from the channels
    all_members list and if owner, owner_members and owner_permissions lists

    Arguments:
    auth_user_id (integer) - id of the user joining the channel
    channel_id (integer) - id of the channel

    Exceptions:
    InputError - Occurs when given:
                    - channel_id does not exist/invalid
    AccessError - Occurs when given:
                    - Authorised user is not a member of the channel

    Return value:
        Returns an empty dictionary when user successfully leaves the channel
    """
    
    # Find channel corresponding to channel_id
    store = data_store.get()
    valid_channel = list(filter(lambda channel: channel["id"] == channel_id, store["channels"]))
    if not valid_channel:
        raise InputError(description="Invalid channel id")
    # Check if auth user id is in the members list
    if auth_user_id not in valid_channel[0]["all_members"]:
        raise AccessError(description="Authorised user is not member of the channel")

    # Check if auth user is a owner
    if auth_user_id in valid_channel[0]["owner_members"]:
        valid_channel[0]["owner_members"].remove(auth_user_id)
    
    # Revoke permissions if owner/global owner
    if auth_user_id in valid_channel[0]["owner_permissions"]:
        valid_channel[0]["owner_permissions"].remove(auth_user_id)
    
    valid_channel[0]["all_members"].remove(auth_user_id)
    
    data_store.set(store)
    return {}
    
def channel_removeowner_v1(auth_user_id, channel_id, u_id):
    """
    Removes user with user u_id as an owner of the channel.

    Arguments:
        auth_user_id (integer) - ID of the authorised user demoting.
        channel_id (integer) - ID of the channel requested for channel_addowner.
        u_id (integer) - ID of the user being demoted.
    
    Exceptions:
        InputError - Occurs when:
                        - channel_id does not refer to a valid channel.
                        - u_id does not refer to a valid user
                        - u_id refers to a user who is not an owner of the channel
                        - u_id refers to a user who is currently the only owner of the channel
        AccessError - Occurs when:
                        - channel_id is valid but the authorised user does not
                        have owner permissions for the channel.
    
    Return Value:
        Returns an empty dictionary on success.
    """
    store = data_store.get()
    channels = store["channels"]
    users = store["users"]
    
    # Find channel
    valid_channel = list(filter(lambda channel: channel["id"] == channel_id, channels))

    if not valid_channel:
        raise InputError(description="Channel does not exist")
    
    user = list(filter(lambda user: u_id == user['id'], users))
    
    if not user:
        raise InputError(description="User is not authorised.")

    if auth_user_id not in valid_channel[0]["owner_permissions"]:
        raise AccessError(description="User is not an owner/does not have owner perms")

    if u_id not in valid_channel[0]["owner_members"]:
        raise InputError(description="User is not an owner/does not have owner perms")
    
    if u_id in valid_channel[0]["owner_members"] and len(valid_channel[0]["owner_members"]) == 1:
        raise InputError(description="User is currently the only owner of the channel")
    
    # Removes the owner's u_id from the owner_members list and the owner_permissions list.
    valid_channel[0]["owner_members"].remove(u_id)

    # Checks to see if they're a global owner.
    if user[0]["permission"] != 1:
        valid_channel[0]["owner_permissions"].remove(u_id)
    
    data_store.set(store)

    return {}


