import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import AccessError
from src import config
from src.channels import channels_create_v1, channels_list_v1
from src.data_store import data_store
import json
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1, auth_passwordreset_reset_v1
import jwt
from src.other import clear_v1
from src.channels import channels_listall_v1
from src.channel import channel_join_v1, channel_leave_v1, channel_messages_v1, channel_invite_v1, channel_details_v1, channel_addowner_v1, channel_removeowner_v1
from src.dm import dm_details_v1, dm_create_v1, dm_leave_v1, dm_messages_v1, dm_list_v1, dm_remove_v1
from src.user import list_all_users, user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1, message_share_v1, message_sendlater_v1, message_sendlaterdm_v1, message_pin_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1


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

def check_valid_token_and_session(token):
    """Helper function to check if token is valid and session is valid"""
    sessions = data_store.get()["sessions"]
    user_session = {}
    try:
        user_session = jwt.decode(token, config.hashcode, algorithms=['HS256'])
    except Exception as invalid_jwt:
        raise AccessError(description="Invalid JWT") from invalid_jwt
    if user_session["user_id"] in sessions:
        sess_tok_id = (user_session["session_id"], user_session["token_id"])
        if sess_tok_id not in sessions[user_session["user_id"]]:
            raise AccessError(description="Invalid session")
    else:
        raise AccessError(description="Invalid session")
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
    info = request.get_json()
    user_info = auth_login_v1(info['email'], info['password'])
    save()
    return dumps(user_info)

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
    info = request.get_json()
    check_valid_token_and_session(info["token"])
    auth_logout_v1(info["token"])
    save()
    return dumps({})

# auth/passwordreset/reset/v1
@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def auth_passwordreset_reset():
    data = request.get_json()
    auth_passwordreset_reset_v1(data["reset_code"], data["new_password"])
    save()
    return dumps({})

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
    token = request.args.get("token")
    user_id = check_valid_token_and_session(token)
    channels = channels_list_v1(user_id)
    return dumps(channels)

# channels/listall/v2
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    response = request.args.get("token")
    user_id = check_valid_token_and_session(response)
    channels_info = channels_listall_v1(user_id)
    save()
    return dumps(channels_info)

#====== channel.py =====#

# channel/details/v2
@APP.route("/channel/details/v2", methods=['GET'])
def channel_details():
    response = request.args.to_dict()
    user_id = check_valid_token_and_session(response["token"])
    channel_info = channel_details_v1(user_id, int(response["channel_id"]))
    save()
    return dumps(channel_info)

# channel/join/v2
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    channel_join_v1(user_id, data["channel_id"])  
    save()
    return dumps({})  


# channel/invite/v2
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    data = request.get_json() # { token, channel_id, u_id }
    user_info = check_valid_token_and_session(data["token"])
    channel_invite_v1(user_info, data["channel_id"], data["u_id"])
    return dumps({})

# channel/messages/v2
@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    token = request.args.get("token")
    user_id = check_valid_token_and_session(token)
    channel_messages = channel_messages_v1(user_id, int(request.args.get("channel_id")), int(request.args.get("start")))
    save()
    return dumps(channel_messages)

# channel/leave/v1
@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    channel_leave_v1(user_id, data["channel_id"])
    save()
    return dumps({})

# channel/addowner/v1
@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    response = request.get_json()
    user_id = check_valid_token_and_session(response["token"])
    channel_addowner_v1(user_id, response["channel_id"], response["u_id"])
    save()
    return dumps({})

# channel/removeowner/v1
@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    response = request.get_json()
    user_id = check_valid_token_and_session(response["token"])
    channel_removeowner_v1(user_id, response["channel_id"], response["u_id"])
    save()
    return dumps({})

#====== message.py =====#

# message/send/v1
@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    new_message = message_send_v1(user_id, data["channel_id"], data["message"])
    save()
    return dumps(new_message)

# message/edit/v1
@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    message_edit_v1(user_id, data["message_id"], data["message"])
    save()
    return dumps({})

# message/remove/v1
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    message_remove_v1(user_id, data["message_id"])
    save()
    return dumps({})

# message/senddm/v1
@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    new_dm_message = message_senddm_v1(user_id, data["dm_id"], data["message"])
    save()
    return dumps(new_dm_message)

# message/senddm/v1
@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    message_pin_v1(user_id, data["message_id"])
    save()
    return dumps({})

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    message_id = message_sendlaterdm_v1(user_id, data["dm_id"], data["message"], data["time_sent"])
    save()
    return dumps(message_id)

@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    message_id = message_sendlater_v1(user_id, data["channel_id"], data["message"], data["time_sent"])
    save()
    return dumps(message_id)

@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"])
    shared_message_id = message_share_v1(user_id, data["og_message_id"], data["message"], data["channel_id"], data["dm_id"])
    save()
    return dumps(shared_message_id)

#====== dm.py =====#

# dm/create/v1
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    user_token = data["token"]
    user_lists = data["u_ids"]
    user_id = check_valid_token_and_session(user_token)
    dm_id = dm_create_v1(user_id, user_lists)
    save()
    return dumps(dm_id)
                                                        
# dm/list/v1
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    info = request.args.to_dict()
    info_token = info["token"]
    auth_user_id = check_valid_token_and_session(info_token)
    list_of_dms = dm_list_v1(auth_user_id)
    return dumps(list_of_dms)

# dm/remove/v1
@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    user_id = check_valid_token_and_session(data["token"]) 
    #user_id for valid user 
    dm_id = data["dm_id"]
    dm_remove_v1(user_id, dm_id)
    save()
    return dumps({})

# dm/details/v1
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    response = request.args.to_dict()
    user_id = check_valid_token_and_session(response["token"])
    dm_info = dm_details_v1(user_id, int(response["dm_id"]))
    save()
    return dumps(dm_info)

# dm/leave/v1
@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    response = request.get_json()
    user_id = check_valid_token_and_session(response["token"])
    dm_leave_v1(user_id, response["dm_id"])
    save()
    return dumps({})

# dm/messages/v1
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    token = request.args.get("token")
    user_id = check_valid_token_and_session(token)
    dm_channel_messages = dm_messages_v1(user_id, int(request.args.get("dm_id")), int(request.args.get("start")))
    save()
    return dumps(dm_channel_messages)

#===== user.py =====#

# users/all/v1
@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    token = request.args.get("token")
    check_valid_token_and_session(token)
    users = list_all_users()
    return dumps(users)

# user/profile/v1
@APP.route("/user/profile/v1", methods=['GET'])
def user_profile(): 
    token = request.args.get("token")
    u_id = request.args.get("u_id")
    check_valid_token_and_session(token)
    profile = user_profile_v1(u_id)
    save()
    return dumps({"user": profile})

# user/profile/setname/v1
@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname():
    data = request.get_json()
    first_name = data["name_first"]
    last_name = data["name_last"]
    user_id = check_valid_token_and_session(data["token"])
    user_profile_setname_v1(user_id, first_name, last_name)
    save()
    return dumps({})


# user/profile/setemail/v1
@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail():
    data = request.get_json()
    user_email = data["email"]
    user_id = check_valid_token_and_session(data["token"])
    user_profile_setemail_v1(user_id, user_email)
    save()
    return dumps({})

# user/profile/sethandle/v1
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle():
    data = request.get_json()
    new_handle = data["handle_str"]
    user_id = check_valid_token_and_session(data["token"])
    user_profile_sethandle_v1(user_id, new_handle)
    save()
    return dumps({})

#===== admin.py =====#

# admin/user/remove/v1
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove():
    data = request.get_json()
    auth_user_id = check_valid_token_and_session(data["token"])
    admin_user_remove_v1(auth_user_id, data["u_id"])
    save()
    return dumps({})

# admin/userpermission/change/v1
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change():
    data = request.get_json()
    auth_user_id = check_valid_token_and_session(data["token"])
    admin_userpermission_change_v1(auth_user_id, data["u_id"], data["permission_id"])
    save()
    return dumps({})

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
