from src.data_store import data_store
from src.error import InputError, AccessError
from src.message import message_send_v1, find_item
from src.other import save
from googletrans import Translator, constants
import time, threading
from random_word import RandomWords
from english_words import english_words_lower_set
import random

def commands_translate(target_language, message):
    """
    translates a message into the desired language when given the command:
    /translate target_language message

    Arguments:
    target_language (string) - the language to be translated to
    message (string) - the message to be translated

    Exceptions:
    InputError - Occurs when given:
                    - command is in an incorrect format

    Return value:
        returns the translated message in the format:
        original_message (language) --> translated_message (language)
    """

    translator = Translator()
    if not message:
        raise InputError(description="Invalid use of command, proper usage is: /translate language message")

    try:
        translation = translator.translate(text=message, dest=target_language)
    except ValueError:
        raise InputError(description="Invalid use of command, proper usage is: /translate language message") from InputError
    
    return f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})"

def commands_find_user(handle):
    store = data_store.get()
    users = store['users']
    valid_user = list(filter(lambda user: handle == user['handle'], users))
    return valid_user[0]["id"]
    
def wordbomb_start(channel_id, user_id):
    """
    Starts a wordbomb session when the user enters the command /wordbomb

    Arguments:
    channel_id (integer) - the id of the channel
    user_id (string) - the user who started a wordbomb game

    Exceptions:
    InputError - Occurs when:
                    - channel doesnt exist
    AccessError - Occurs when:
                    - user is not a member of the channel

    Return value:
        none
    """
    store = data_store.get()
    channels = store['channels']

    # Find the given channel
    valid_channel = find_item(channel_id, channels, "id")
    
    # Check if channel id is valid
    if not valid_channel:
        raise InputError(description="Channel doesn't exist")
    
    # Check if auth_user_id is a member of channel
    if user_id not in valid_channel[0]['all_members']:
        raise AccessError(description="This user is not a member of this channel.")
    
    valid_channel[0]["wordbomb"]["active"] = True
    valid_channel[0]["wordbomb"]["user_turn"] = user_id
    
    lives_dict = {}
    for user in valid_channel[0]["all_members"]:
        lives_dict[user] = 2

    valid_channel[0]["wordbomb"]["lives"] = lives_dict


    data_store.set(store)
    return

def wordbomb_active(channel_id, user_id):
    """
    checks if there is an active wordbomb session

    Arguments:
    channel_id (integer) - the id of the channel
    user_id (string) - the user who started a wordbomb game

    Exceptions:
    InputError - Occurs when:
                    - channel doesnt exist
    AccessError - Occurs when:
                    - user is not a member of the channel

    Return value:
        boolean - True if there is an active session, False otherwise
    """
    store = data_store.get()
    channels = store['channels']

    # Find the given channel
    valid_channel = find_item(channel_id, channels, "id")
    
    # Check if channel id is valid
    if not valid_channel:
        raise InputError(description="Channel doesn't exist")
    
    # Check if auth_user_id is a member of channel
    if user_id not in valid_channel[0]['all_members']:
        raise AccessError(description="This user is not a member of this channel.")
    
    return valid_channel[0]["wordbomb"]["active"]


def wordbomb_send(channel_id, message, user_id):
    """
    Starts a wordbomb session when the user enters the command /wordbomb

    Arguments:
    channel_id (integer) - the id of the channel
    message (string) - the message the user entered

    Exceptions:
        None

    Return value:
        boolean - True if the word is valid, False 
    """
    store = data_store.get()
    channels = store['channels']
    valid_channel = find_item(channel_id, channels, "id")
    message = message.lower()
    if valid_channel[0]["wordbomb"]["user_turn"] != user_id:
        return False
    
    if valid_channel[0]["wordbomb"]["bomb_str"] in message and message in english_words_lower_set:
        return True
    else:
        return False


def wordbomb_next_bomb(channel_id, user_id):
    """
    Generates a 'bomb' for the next user

    Arguments:
    channel_id (integer) - the id of the channel
    user_id (integer) - the user who started a wordbomb game 
                        or sent the most recent message

    Exceptions:
        None

    Return value:
        next_bomb_msg - contains an ascii art of a bomb containing the
        word to be guessed
    """
    r = RandomWords()
    random_word = r.get_random_word()
    while len(random_word) < 3 or not random_word.isalpha():
        random_word = r.get_random_word()
    
    substring_len = random.randint(2,3)
    substring_start = random.randint(0,len(random_word)-substring_len)
    
    substring = random_word[int(substring_start):int(substring_start+substring_len)]

    store = data_store.get()
    channels = store['channels']

    valid_channel = find_item(channel_id, channels, "id")
    
    

    current_user_pos = valid_channel[0]["all_members"].index(user_id)

    if len(valid_channel[0]["all_members"]) == current_user_pos+1:
        current_user_pos = 0
    else:
        current_user_pos += 1

    valid_channel[0]["wordbomb"]["user_turn"] = valid_channel[0]["all_members"][current_user_pos]
    valid_user = find_item(valid_channel[0]["wordbomb"]["user_turn"], store['users'], "id")
    handle = valid_user[0]["handle"]
    valid_channel[0]["wordbomb"]["bomb_str"] = substring
    valid_channel[0]["wordbomb"]["turn_count"] += 1

    next_bomb_msg = (f"""\
Word Bomb
{handle}'s Turn
                        \|/
                       .-*-         
                      / /|\         
                   _ L _            
              ,  "          "  .          
            /                    \      
                     {substring}    
           |                      |
            \                    /        
              "  ,_____,  "  
                """)

    turn_count = valid_channel[0]["wordbomb"]["turn_count"]
    explode_timer = threading.Timer(8, wordbomb_explode, args=(channel_id, valid_channel[0]["wordbomb"]["user_turn"], turn_count))
    explode_timer.start()

    data_store.set(store)
    return next_bomb_msg

def wordbomb_explode(channel_id, user_id, turn_count):
    """
    Threading function: 8 seconds after a wordbomb_next_bomb is called
    this function is called, if it is still the same turn as when the thread
    was started the bomb will explode and the player will lose

    Arguments:
    channel_id (integer) - the id of the channel
    user_id (integer) - the user whose turn it was when the thread was started

    Exceptions:
        None

    Return value:
        none
    """
    store = data_store.get()
    channels = store['channels']

    # Find the given channel
    valid_channel = find_item(channel_id, channels, "id")

    if turn_count != valid_channel[0]["wordbomb"]["turn_count"]:
        return

    
    valid_channel[0]["wordbomb"]["lives"][user_id] -= 1

    win_condition = 0
    for key, value in valid_channel[0]["wordbomb"]["lives"].items():
        if value == 0:
            win_condition += 1
        else:
            winning_player = key

    if win_condition + 1 == len(valid_channel[0]["wordbomb"]["lives"]):
        valid_channel[0]["wordbomb"]["active"] = False
        valid_user = find_item(winning_player, store['users'], "id")
        handle = valid_user[0]["handle"]
        win_msg = (f"""\
Word Bomb
{handle} won the game!
     _ . - ^ ^ - - - . . . . , , - -        
 _--                                 - - _  
<           GAME OVER        >)
|                                             | 
 \._                                    _ ./  
    ```--. . , ; .                  --'''       
                   |   | |   |             
                 .-=||  | |=-.   
            `-=#$%&%$#=-'   
                      | ;  :|     
 _____.,-#%&$@%#&#~,._____
                """)
        message_send_v1(user_id, channel_id, win_msg)
        data_store.set(store)
        save()
        return


    
    
    data_store.set(store)
    save()
    next_bomb_msg = wordbomb_next_bomb(channel_id, user_id)
    message_send_v1(user_id, channels, next_bomb_msg)
    return

