from src.data_store import data_store
from src.error import InputError, AccessError
from src.message import message_send_v1, find_item
from src.other import save
from googletrans import Translator, constants
import time, threading

def commands_translate(target_language, message):
    translator = Translator()
    if not message:
        raise InputError(description="Invalid use of command, proper usage is: /translate language message")

    try:
        translation = translator.translate(message, dest=target_language)
    except ValueError:
        raise InputError(description="Invalid use of command, proper usage is: /translate language message")
    
    return f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})"
    