import tests.route_helpers as rh
import pytest, time

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()['token']

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

    # test time stamp does not change if nothing changes i.e. no new channels, dms, messages
    workspace_2 = rh.users_stats(clear_and_register).json()["workspace_stats"]
    assert len(workspace_1["channels_exist"]) == 1
    assert len(workspace_1["dms_exist"]) == 1
    assert len(workspace_1["messages_exist"]) == 1

# Metrics for channels and dms work
def test_first_user_join_channel_dm(clear_and_register):
    rh.channels_create(clear_and_register, "channel", True)
    channel_time_stamp = time.time()
    rh.dm_create(clear_and_register, [])
    dm_time_stamp = time.time()

    workspace = rh.users_stats(clear_and_register).json()["workspace_stats"]
    # two time stamps because 1 when first user registers and second comes from create 
    # new channel/dm
    assert len(workspace["channels_exist"]) == 2
    assert workspace["channels_exist"][-1]["num_channels_exist"] == 1
    assert abs(workspace["channels_exist"][-1]["time_stamp"] - channel_time_stamp) < 2

    assert len(workspace["dms_exist"]) == 2
    assert workspace["dms_exist"][-1]["num_dms_exist"] == 1
    assert abs(workspace["dms_exist"][-1]["time_stamp"] - dm_time_stamp) < 2

    assert len(workspace["messages_exist"]) == 1
    
    assert workspace["utilization_rate"] == 1

# Metrics for messages works
def test_workspace_messages_metrics(clear_and_register):
    channel_id = rh.channels_create(clear_and_register, "channel", True).json()["channel_id"]
    rh.message_send(clear_and_register, channel_id, "hello")
    time_message_1 = time.time()
    rh.message_send(clear_and_register, channel_id, "hello")
    time_message_2 = time.time()
    rh.message_send(clear_and_register, channel_id, "hello")
    time_message_3 = time.time()
    rh.message_send(clear_and_register, channel_id, "hello")
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
def test_utilization_rate_change(clear_and_register):
    rh.dm_create(clear_and_register, [])

    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 1

    rh.auth_register("random2@gmail.com", "123abc!@#", "Bob", "Smith")

    assert rh.users_stats(clear_and_register).json()["workspace_stats"]["utilization_rate"] == 0.5

# Number of messages and dms decrease if they are removed
# def test_num_dms_messages_decrease(clear_and_register):
#     dm_id = rh.dm_create(clear_and_register, []).json()["dm_id"]
#     channel_id = rh.channels_create(clear_and_register, "channel", True).json()["channel_id"]
#     rh.message_senddm(clear_and_register, dm_id, "hello")
#     rh.message_senddm(clear_and_register, dm_id, "hello")
#     rh.message_senddm(clear_and_register, dm_id, "hello")

#     rh.message_send(clear_and_register, channel_id, "hello")
#     removing_message_id = rh.message_send(clear_and_register, channel_id, "hello").json()["message_id"]

#     workspace = rh.users_stats(clear_and_register).json()["workspace_stats"]
#     assert workspace["dms_exist"][-1]["num_dms_exists"] == 1
#     assert workspace["messages_exist"][-1]["num_messages_exist"] == 5

#     rh.dm_remove(clear_and_register, dm_id)
#     rh.message_remove(clear_and_register, removing_message_id)

#     workspace = rh.users_stats(clear_and_register).json()["workspace_stats"]
#     assert workspace["dms_exist"][-1]["num_dms_exists"] == 0
#     assert workspace["messages_exist"][-1]["num_messages_exist"] == 1

# Invalid inputs

# Invalid token
def test_invalid_token(clear_and_register):
    assert rh.users_stats(clear_and_register + 'invalidtoken').status_code == 403

# Invalid session
def test_invalid_session(clear_and_register):
    rh.auth_logout(clear_and_register)
    assert rh.users_stats(clear_and_register).status_code == 403

