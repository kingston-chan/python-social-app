from os import error
import sys
import signal
from json import dumps
from flask import Flask, request
from requests.models import DecodeError
from requests.sessions import session
from flask_cors import CORS
from src.error import InputError, AccessError
from src import config
from src.channels import channels_create_v1
from src.data_store import data_store
import json
from src.auth import auth_register_v1
import jwt
from src.other import clear_v1
from src.channel import channel_messages_v1

HASHCODE = "LKJNJLKOIHBOJHGIUFUTYRDUTRDSRESYTRDYOJJHBIUYTF"

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)


#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
# @APP.route("/echo", methods=['GET'])
# def echo():
#     data = request.args.get('data')
#     if data == 'echo':
#    	    raise InputError(description='Cannot echo "echo"')
#     return dumps({
#         'data': data
#     })


def check_valid_token_and_session(token):
    """Helper function to check if token is valid and session is valid"""
    sessions = data_store.get()["sessions"]
    user_session = {}
    try:
        user_session = jwt.decode(token, HASHCODE, algorithms=['HS256'])
    except Exception as invalid_jwt:
        raise AccessError("Invalid JWT") from invalid_jwt
    if not user_session["session_id"] in sessions[user_session["user_id"]]:
        raise AccessError("Invalid session")
    return user_session["user_id"]

def save():
    store = data_store.get()
    with open("datastore.json", "w") as FILE:
        json.dump(store, FILE)
    
data = {}

try:
    data = json.load(open("datastore.json", "r"))
except Exception:
    pass

if data:
    data_store.set(data)

#====== auth.py =====#

# auth/login/v2
@APP.route("/auth/login/v2", methods=['POST'])
def auth_login():
    return {}

# auth/register/v2
@APP.route("/auth/register/v2", methods=['POST'])
def auth_register():
    info = request.get_json()
    user_info = auth_register_v1(info['email'], info['password'], info['name_first'], info['name_last'])
    save()
    return dumps(user_info)


# auth/logout/v1
@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    return {}

#====== channels.py =====#

# channels/create/v2
@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    new_channel = channels_create_v1(user_id, data["name"], data["is_public"])
    save()
    return dumps(new_channel)

# channels/list/v2
@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    return {}

# channels/listall/v2
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    return {}

#====== channel.py =====#

# channel/details/v2
@APP.route("/channel/details/v2", methods=['GET'])
def channel_details():
    return {}

# channel/join/v2
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    return {}

# channel/invite/v2
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    return {}

# channel/messages/v2
@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    channel_messages = channel_messages_v1(user_id, data["channel_id"], data["start"])
    save()
    return dumps(channel_messages)

# channel/leave/v1
@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    return {}

# channel/addowner/v1
@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    return {}

# channel/removeowner/v1
@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    return {}

#====== message.py =====#

# message/send/v1
@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    return {}

# message/edit/v1
@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    return {}

# message/remove/v1
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    return {}

# message/senddm/v1
@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    return {}

#====== dm.py =====#

# dm/create/v1
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    return {}

# dm/list/v1
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    return {}

# dm/remove/v1
@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    return {}

# dm/details/v1
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    return {}

# dm/leave/v1
@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    return {}

# dm/messages/v1
@APP.route("/dm/messages/v1", methods=['GET'])
def login():
    return {}

#===== users.py =====#

# users/all/v1
@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    return {}

#===== user.py =====#

# user/profile/v1
@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    return {}

# user/profile/setname/v1
@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname():
    return {}

# user/profile/setemail/v1
@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail():
    return {}

# user/profile/sethandle/v1
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle():
    return {}

#===== admin.py =====#

# admin/user/remove/v1
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove():
    return {}

# admin/userpermission/change/v1
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change():
    return {}

# clear/v1
@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    save()
    return dumps({})

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
