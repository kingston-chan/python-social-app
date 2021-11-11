import tests.route_helpers as rh
import pytest, time

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()['token']

@pytest.fixture
def create_channel(clear_and_register):
    return rh.channels_create(clear_and_register, "channel", True).json()["channel_id"]

@pytest.fixture
def create_dm(clear_and_register):
    return rh.dm_create(clear_and_register, []).json()["dm_id"]

# Valid inputs

# Metrics when first user registers and does not join dm or channel
def test_first_user_registers(clear_and_register):
    workspace_1 = rh.users_stats(clear_and_register).json()["workspace_stats"]
    assert len(workspace_1["channels_exist"]) == 1
    assert workspace_1["channels_exist"][-1]["num_channels_exist"] == 0
    assert len(workspace_1["dms_exist"]) == 1
    assert workspace_1["dms_exist"][-1]["num_dms_exist"] == 0
    assert len(workspace_1["messages_exist"]) == 1
    assert workspace_1["messages_exist"][-1]["num_messages_exist"] == 0
    assert workspace_1["utilization_rate"] == 0
    assert type(workspace_1["utilization_rate"]) is float

    # test time stamp does not change if nothing changes i.e. no new channels, dms, messages
    workspace_2 = rh.users_stats(clear_and_register).json()["workspace_stats"]
    assert len(workspace_2["channels_exist"]) == 1
    assert len(workspace_2["dms_exist"]) == 1
    assert len(workspace_2["messages_exist"]) == 1

# Metrics for channels and dms work
def test_first_user_join_channel_dm(clear_and_register, create_channel, create_dm):
    workspace = rh.users_stats(clear_and_register).json()["workspace_stats"]
    # two time stamps because 1 when first user registers and second comes from create 
    # new channel/dm
    assert len(workspace["channels_exist"]) == 2
    assert workspace["channels_exist"][-1]["num_channels_exist"] == 1

    assert len(workspace["dms_exist"]) == 2
    assert workspace["dms_exist"][-1]["num_dms_exist"] == 1

    assert len(workspace["messages_exist"]) == 1
    
    assert workspace["utilization_rate"] == 1
    assert type(workspace["utilization_rate"]) is float

# Metrics for messages works
def test_workspace_messages_metrics(clear_and_register, create_channel):
    rh.message_send(clear_and_register, create_channel, "hello")
    time_message_1 = time.time()
    rh.message_send(clear_and_register, create_channel, "hello")
    time_message_2 = time.time()
    rh.message_send(clear_and_register, create_channel, "hello")
    time_message_3 = time.time()
    rh.message_send(clear_and_register, create_channel, "hello")
    time_message_4 = time.time()

    workspace = rh.users_stats(clear_and_register).json()["workspace_stats"]
    # seperate time stamp for each message sent
    assert len(workspace["messages_exist"]) == 5

    assert workspace["messages_exist"][0]["num_messages_exist"] == 0
    assert workspace["messages_exist"][1]["num_messages_exist"] == 1
    assert workspace["messages_exist"][2]["num_messages_exist"] == 2
    assert workspace["messages_exist"][3]["num_messages_exist"] == 3
    assert workspace["messages_exist"][4]["num_messages_exist"] == 4

    assert abs(workspace["messages_exist"][1]["time_stamp"] - time_message_1) < 2
    assert abs(workspace["messages_exist"][2]["time_stamp"] - time_message_2) < 2
    assert abs(workspace["messages_exist"][3]["time_stamp"] - time_message_3) < 2
    assert abs(workspace["messages_exist"][4]["time_stamp"] - time_message_4) < 2
    
    assert workspace["utilization_rate"] == 1

# Utilization rate changes correctly
def test_utilization_rate_change(clear_and_register, create_dm):
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 1
    rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith")
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 0.5

# Number of messages and dms decrease if they are removed
def test_num_dms_messages_decrease(clear_and_register, create_dm, create_channel):
    rh.message_senddm(clear_and_register, create_dm, "hello")
    rh.message_senddm(clear_and_register, create_dm, "hello")
    rh.message_senddm(clear_and_register, create_dm, "hello")

    og_msg = rh.message_send(clear_and_register, create_channel, "hello").json()["message_id"]
    removing_message_id = rh.message_send(clear_and_register, create_channel, "hello").json()["message_id"]

    workspace = rh.users_stats(clear_and_register).json()["workspace_stats"]
    assert workspace["dms_exist"][-1]["num_dms_exist"] == 1
    assert workspace["messages_exist"][-1]["num_messages_exist"] == 5

    rh.dm_remove(clear_and_register, create_dm)
    rh.message_remove(clear_and_register, removing_message_id)
    rh.message_edit(clear_and_register, og_msg, "bye")
    rh.message_share(clear_and_register, og_msg, "hello", create_channel, -1)

    workspace = rh.users_stats(clear_and_register).json()["workspace_stats"]
    assert workspace["dms_exist"][-1]["num_dms_exist"] == 0
    assert len(workspace["messages_exist"]) == 11
    assert workspace["messages_exist"][-1]["num_messages_exist"] == 2

# Utilization increases if removed user is not in a dm/channel
def test_utilization_stays_same(clear_and_register, create_channel):
    uid2 = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()["auth_user_id"]
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 0.5
    rh.admin_user_remove(clear_and_register, uid2)
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 1

# Utilization rate changes when users leave channels/dms and join/get invited channels
def test_utilization_change_when_leaving_channel_dm(clear_and_register, create_channel):
    user2 = rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith").json()
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 0.5

    dm_id = rh.dm_create(clear_and_register, [user2["auth_user_id"]]).json()["dm_id"]
    # Test dm leave
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 1
    rh.dm_leave(user2["token"], dm_id)
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 0.5

    # Test channel invite/leave/join
    rh.channel_invite(clear_and_register, create_channel, user2["auth_user_id"])
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 1
    rh.channel_leave(user2["token"], create_channel)
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 0.5
    rh.channel_join(user2["token"], create_channel)
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 1

# Workspace changes only when messages are sent
def test_workspace_stats_with_delayed_messages(clear_and_register, create_channel, create_dm):
    # Send a message in the dm and channel in three seconds
    rh.message_sendlater(clear_and_register, create_channel, "hello", int(time.time()) + 3)
    rh.message_sendlaterdm(clear_and_register, create_dm, "hello", int(time.time()) + 4)

    assert len(rh.users_stats(clear_and_register).json()["workspace_stats"]["messages_exist"]) == 1
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["messages_exist"][-1]["num_messages_exist"] == 0

    time.sleep(4)
    assert len(rh.users_stats(clear_and_register).json()["workspace_stats"]["messages_exist"]) == 3
    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["messages_exist"][-1]["num_messages_exist"] == 2

# Invalid inputs

# Invalid token
def test_invalid_token(clear_and_register):
    assert rh.users_stats(clear_and_register + 'invalidtoken').status_code == 403

# Invalid session
def test_invalid_session(clear_and_register):
    rh.auth_logout(clear_and_register)
    assert rh.users_stats(clear_and_register).status_code == 403

