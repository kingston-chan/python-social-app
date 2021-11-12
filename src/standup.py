from src.data_store import data_store
from src.error import InputError, AccessError
from src.message import message_send_v1, find_item
from src.user import users_stats_v1, user_stats_v1
from src.other import save
import time
import threading

def standup_thread_send_msg(auth_user_id, channel_id):
    """Helper function to send buffered standup messages when standup ends"""
    store = data_store.get()
    channels = store['channels']
    users = store['users']

    # Channel will always be valid as checked before
    channel = find_item(channel_id, channels, "id")[0]
    
    # Format all standup message into a whole message
    message = "\n".join(channel["standup_queue"])
    

    # Set channel's standup back to inactive and save values
    channel["standup"]["active"] = False
    channel["standup"]["time_finish"] = None
    channel["standup_queue"] = []
    data_store.set(store)
    
    # Check if no messages are sent during standup
    if not message:
        return

    # Send message
    message_send_v1(auth_user_id, channel_id, message)
    
    # Increase auth_user's message count for user stats
    auth_user = find_item(auth_user_id, users, "id")
    auth_user[0]["message_count"] += 1 
    data_store.set(store)
    
    # Check user/workspace stats
    users_stats_v1()
    user_stats_v1(auth_user_id)
    save()
    return

def standup_start_v1(auth_user_id, channel_id, length):
    """
    Start a standup in a channel for length seconds, all messages sent
    will be buffered in a queue

    Arguments: 
        auth_user_id (integer) - ID of the user starting the standup
        channel_id (integer) - ID of the channel where the standup is 
        length (integer) - Duration of standup in seconds

    Exceptions:
        InputError when any of:
        - channel_id does not refer to a valid channel
        - length is a negative integer
        - an active standup is currently running in the channel
      
      AccessError when:
        - channel_id is valid and the authorised user is not a member of the channel
        
    Return Value:
        Returns a dictionary with the time the standup will finish as a integer unix 
        timestamp if successful in starting a time up in given channel
    """
    store = data_store.get()
    channels = store['channels']
    time_finish = int(time.time()) + length
    
    # Find the given channel
    valid_channel = find_item(channel_id, channels, "id")
    
    # Check if channel id is valid
    if not valid_channel:
        raise InputError(description="Channel doesn't exist")
    
    # Check if auth_user_id is a member of channel
    if auth_user_id not in valid_channel[0]['all_members']:
        raise AccessError(description="This user is not a member of this channel.")

    # Check duration of standup is greater than 0
    if length < 0:
        raise InputError(description="Length is a negative integer")
    
    # Check if a standup is already active
    if valid_channel[0]["standup"]["active"]:
        raise InputError(description="Standup already active")
    
    # Set channel is standup
    valid_channel[0]["standup"]["active"] = True
    valid_channel[0]["standup"]["auth_user_id"] = auth_user_id
    valid_channel[0]["standup"]["time_finish"] = time_finish

    # Create a thread to execute sending all buffered messages when duration of standup ends
    standup = threading.Timer(length, standup_thread_send_msg, args=(auth_user_id, channel_id))
    standup.start()

    data_store.set(store)

    return {'time_finish': time_finish}

def standup_active_v1(auth_user_id, channel_id):
    """
    Determine whether a standup in a channel is currently active

    Arguments: 
        auth_user_id (integer) - ID of the user checking whether a standup is active
        channel_id (integer) - ID of the channel where the standup is 

    Exceptions:
        InputError when any of:
        - channel_id does not refer to a valid channel
      
      AccessError when:
        - channel_id is valid and the authorised user is not a member of the channel
        
    Return Value:
        Returns a dictionary with whether or not the a standup is active for the channel, and
        an integer unix time stamp if standup is active otherwise None
    """
    store = data_store.get()
    channels = store['channels']

    # Check given channel id is integer
    try:
        channel_id = int(channel_id)
    except ValueError:
        raise InputError(description="Channel doesn't exist") from InputError
    
    valid_channel = find_item(channel_id, channels, "id")
    
    # Check if channel id is valid
    if not valid_channel:
        raise InputError(description="Channel doesn't exist")
    
    # Check if auth_user_id is a member of channel
    if auth_user_id not in valid_channel[0]['all_members']:
        raise AccessError(description="This user is not a member of this channel.")
    
    data_store.set(store)

    return {
        'is_active': valid_channel[0]["standup"]["active"],
        # Set time finish to None if standup is not active
        'time_finish': valid_channel[0]["standup"]["time_finish"]
    }

def standup_send_v1(auth_user_id, channel_id, message):
    """
    Send a message during a standup

    Arguments: 
        auth_user_id (integer) - ID of the user sending the message during a standup
        channel_id (integer) - ID of the channel where the standup is 
        message (string) - Message the user sent during standup
        
    Exceptions:
        InputError when any of:
        - channel_id does not refer to a valid channel
        - length of message is over 1000 characters
        - an active standup is not currently running in the channel
      
      AccessError when:
        - channel_id is valid and the authorised user is not a member of the channel
        
    Return Value:
        Returns an empty dictionary on successful message sent
    """
    store = data_store.get()
    channels = store['channels']
    users = store['users']

    # Find handle of sender of message
    user_handle = find_item(auth_user_id, users, "id")[0]["handle"]
    
    # Format into standup message
    joined_msg = f"{user_handle}: {message}"
    
    valid_channel = find_item(channel_id, channels, "id")

    # Check if channel id is valid
    if not valid_channel:
        raise InputError(description="Channel doesn't exist")
    
    # Check if auth_user_id is a member of channel
    if auth_user_id not in valid_channel[0]['all_members']:
        raise AccessError(description="This user is not a member of this channel.")
    
    # Check if standup is active
    if not valid_channel[0]["standup"]["active"]:
        raise InputError(description="Standup is not running")
    
    # Check if length of message is invalid
    if len(message) > 1000:
        raise InputError(description="Message is over 1000 characters")
    
    # Store message in buffered queue
    valid_channel[0]["standup_queue"].append(joined_msg)

    data_store.set(store)
    return


    
