from src.data_store import data_store
from src.error import InputError
from src.channel import output_message

def find_message_with_query(user_id, message_list, id_list, query, type_of_id):
    """Helper function to find messages that contain query"""
    # Find messages that belong to channel/dm
    valid_msgs = filter(lambda msg: msg[type_of_id] in id_list, message_list)
    # Within these messages find messages that contain query
    query_msgs = filter(lambda msg: query in msg["message"], valid_msgs)
    # Return a list with output format
    return list(map(lambda msg: output_message(msg, user_id), query_msgs))

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

    # Check channel messages that contain query
    messages_with_query = find_message_with_query(auth_user_id, store["channel_messages"], users_channels_id, query, "channel_id")
    # Check dm messages that contain query
    messages_with_query.extend(find_message_with_query(auth_user_id, store["dm_messages"], users_dms_id, query, "dm_id"))

    return { 
        "messages": messages_with_query
    }

    