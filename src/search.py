from src.data_store import data_store
from src.error import InputError

def search_v1(auth_user_id, query):
    """
    Given a query string, return a collection of messages in all of the channels/DMs 
    that the user has joined that contain the query.

    Arguments: 
        auth_user_id (integer) - id of user in which we are trying to find messages that match query for all 
                                 channels and dms they have joined
        query (string) - string that we want to match messages to

    Exceptions:
        InputError - Occurs when given:
                        - query is less than 1 or over 1000 characters

    Return Value:
        Return a list of dictionaries containing message_id, u_id, message, time_created, reacts and is_pinned
        if query is valid and has found messages that contain query.
                        
    """
    # Check if length of query is valid
    if len(query) < 1 or len(query) > 1000:
        raise InputError(description="Invalid query length")
    
    store = data_store.get()
    # Get list of all the channel and dm ids the user is a part of
    users_channels_id = [channel["id"] for channel in store["channels"] if auth_user_id in channel["all_members"]]
    users_dms_id = [dm["dm_id"] for dm in store["dms"] if auth_user_id in dm["members"]]

    messages_with_query = []
    # Check channel messages that contain query
    find_message_with_query(store["channel_messages"], users_channels_id, messages_with_query, query, "channel_id")
    # Check dm messages that contain query
    find_message_with_query(store["dm_messages"], users_dms_id, messages_with_query, query, "dm_id")

    return { 
        "messages": messages_with_query
    }


def message_output(msg):
    """Helper function to change message to output_message"""
    return {
        "message_id": msg["message_id"], 
        "u_id": msg["u_id"], 
        "message": msg["message"], 
        "time_created": msg["time_created"], 
        "reacts": msg["reacts"], 
        "is_pinned": msg["is_pinned"]
    }

def find_message_with_query(message_list, dm_or_channel_id_list, list_to_store, query, type_of_id):
    """Helper function to find messages that contain query"""
    for msg in message_list:
        if msg[type_of_id] in dm_or_channel_id_list and query in msg["message"]:
            list_to_store.append(message_output(msg))