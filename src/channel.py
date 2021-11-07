"""
Various methods to interact with channels such as inviting users to the channel,
returning the details of the channel, joining channels and returning messages 
of the channel
"""

from src import notifications
from src.error import InputError, AccessError
from src.data_store import data_store

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

    valid_channel = 0
    valid_user = 0
    #checks for valid channel
    for channel in channels:
        if channel_id == channel['id']:
            valid_channel = 1
            #checks to see authorised member is sending channel invitation
            if auth_user_id not in channel['all_members']: 
                raise AccessError(description="not authorised user")
            break
    if valid_channel == 0:
        raise InputError(description="not valid channel ID")   
    #checks for valid user 
    for user in users:
        if u_id == user['id'] and user["email"] is not None and user["handle"] is not None:
            valid_user = 1
            break
    
    if valid_user == 0:
        raise InputError(description="not valid user")
    #checks to see if member
    if u_id in channel['all_members']:
        raise InputError(description="already member")
   
    channel['all_members'].append(u_id)
    
    if user['permission'] == 1:
        channel['owner_permissions'].append(u_id)
    

    user_inviting = list(filter(lambda x : auth_user_id == x["id"], store["users"]))
    channel = list(filter(lambda x : channel_id == x["id"], store["channels"]))

    notif_string = "{} added you to {}".format(user_inviting[0]["handle"],channel[0]["name"])
    notification = {"channel_id" : channel_id, "dm_id": -1, "notification_message": notif_string}
    
    if u_id in store["notifications"]:
        store["notifications"][u_id].append(notification)
    else:
        store["notifications"][u_id] = [notification]

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
    channel_details = {}
    
    channel_exists = False
    owner_ids = None
    all_members_ids = None

    # Searches for a channel with the same ID and stores its information.
    # Also checks if a channel exists.
    for channel in channels:
        if channel["id"] == channel_id:
            channel_exists = True
            channel_details["name"] = channel["name"]
            channel_details["is_public"] = channel["is_public"]
            channel_details["owner_members"] = []
            channel_details["all_members"] = []
            # channel["owner_members"] and channel["all_members"] are lists of user IDs.
            owner_ids = channel["owner_members"]
            all_members_ids = channel["all_members"]

    if not channel_exists:
        raise InputError(description="Channel does not exist") 
    
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

    an_invited_member = False
    members = channel_details["all_members"]

    # Checks if the user is apart of the channel.
    for member in members:
        if member["u_id"] == auth_user_id:
            an_invited_member = True

    if not an_invited_member:
        raise AccessError(description="User is not a member of the channel")

    return channel_details

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
    channel_valid = False
    start_valid = False
    selected_channel = {}
    store = data_store.get()
    channels = store['channels']
    channel_messages = store['channel_messages']

    # Scans if the channel exists.
    for channel in channels:
        if channel['id'] == channel_id:
            channel_valid = True
            # Checks if the start value is valid within the length of 
            # messages in the channel.
            if start <= len(list(filter(lambda x: (x['channel_id'] == channel_id), channel_messages))):
                start_valid = True
                selected_channel = channel  # Channel is also selected

    # If the channel_id or start value are invalid, then errors are raised.
    if channel_valid is False:
        raise InputError(description="This channel is not valid.")
    if start_valid is False:
        raise InputError(description="This start is not valid.")
    
    # Checks if the authorised user is a member of the channel.
    member_valid = False
    for member in selected_channel['all_members']:
        if member == auth_user_id:
            member_valid = True

    # If the user is not a member, then an error is raised.
    if member_valid is False:
        raise AccessError(description='User is not authorised.')

    # The channel is scanned for its messages.

    selected_channel_messages = []

    if channel_messages == []:
        length = 0
    else:
        selected_channel_messages = list(filter(lambda x: (x['channel_id'] == channel_id), channel_messages))
        selected_channel_messages.reverse()
        length = len(selected_channel_messages)

    index = start
    counter = 0
    selected_messages = []
    while index < length and counter < 50:
        selected_messages.append(selected_channel_messages[index])
        index += 1
        counter += 1

    # If the scanner hits the end of the messages, the end is -1
    # else, the end is the final message index.
    if index == length:
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

    user = list(filter((lambda user: user["id"] == auth_user_id), users))[0]
    
    # Check if channel is valid
    channel_exists = 0
    for channel in channels:
        if channel_id == channel['id']:
            channel_exists = 1
            break
        
    if not channel_exists:
        raise InputError(description="Invalid Channel ID")
    
    if auth_user_id in channel['all_members']:
        raise InputError(description="Already a member of channel")

    # Global members cannot join private channels
    if channel['is_public'] is False and user['permission'] == 2:
        raise AccessError(description="Channel is private")
    
    # Give channel owner permissions to global owners
    if user['permission'] == 1:
        channel['owner_permissions'].append(auth_user_id)
    
    channel['all_members'].append(auth_user_id)
    
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

    # Checks if a user exists.
    user_exists = False
    for user in users:
        if u_id == user['id']:
            user_exists = True
            break
    
    if not user_exists:
        raise InputError(description="User is not authorised.")

    channel_exists = False
    owner_ids = None
    all_members_ids = None
    owner_perms_ids = None

    # Searches for a channel with the same ID and stores its information.
    # Also checks if a channel exists.
    for channel in channels:
        if channel["id"] == channel_id:
            channel_exists = True
            # channel["owner_members"], channel["all_members"] and
            # channel["owner_permissions"] are lists of user IDs.
            owner_ids = channel["owner_members"]
            all_members_ids = channel["all_members"]
            owner_perms_ids = channel["owner_permissions"]

    if not channel_exists:
        raise InputError(description="Channel does not exist") 
    
    if auth_user_id not in owner_ids and auth_user_id not in owner_perms_ids:
        raise AccessError(description="User is not an owner/does not have the owner permissions.")

    if u_id not in all_members_ids:
        raise InputError(description="User is not a member of the channel")

    if u_id in owner_ids:
        raise InputError(description="User is already an owner of the channel")

    # Assigns the new owner's u_id to the owner_members list and the owner_permissions list.
    owner_ids.append(u_id)

    # Checks if they're a global owner.
    if u_id not in owner_perms_ids:
        owner_perms_ids.append(u_id)

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
    store = data_store.get()
    for channel in store["channels"]:
        # Find channel corresponding to channel_id
        if channel["id"] == channel_id:
            # Check if auth user id is in the members list
            if auth_user_id in channel["all_members"]:
                # Check if auth user is a owner
                if auth_user_id in channel["owner_members"]:
                    channel["owner_members"].remove(auth_user_id)
                # Revoke permissions if owner/global owner
                if auth_user_id in channel["owner_permissions"]:
                    channel["owner_permissions"].remove(auth_user_id)
                channel["all_members"].remove(auth_user_id)
            else:
                raise AccessError(description="Authorised user is not member of the channel")
            data_store.set(store)
            return {}
    raise InputError(description="Invalid channel id")
    
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
    
    owner_ids = None
    owner_perms_ids = None

    # Checks if a channel exists
    channel_exists = False
    for channel in channels:
        if channel["id"] == channel_id:
            channel_exists = True
            owner_ids = channel["owner_members"]
            owner_perms_ids = channel["owner_permissions"]

    if not channel_exists:
        raise InputError(description="Channel does not exist")
    
    # Checks if a user exists
    user_exists = False
    user_permission = None
    for user in users:
        if u_id == user['id']:
            user_exists = True
            user_permission = user["permission"]
            break
    
    if not user_exists:
        raise InputError(description="User is not authorised.")

    if auth_user_id not in owner_ids and auth_user_id not in owner_perms_ids:
        raise AccessError(description="User is not an owner/does not have owner perms")

    if u_id not in owner_ids and u_id not in owner_perms_ids:
        raise InputError(description="User is not an owner/does not have owner perms")
    
    if u_id in owner_ids and len(owner_ids) == 1:
        raise InputError(description="User is currently the only owner of the channel")
    
    # Removes the owner's u_id from the owner_members list and the owner_permissions list.
    owner_ids.remove(u_id)

    # Checks to see if they're a global owner.
    if user_permission != 1:
        owner_perms_ids.remove(u_id)
    
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