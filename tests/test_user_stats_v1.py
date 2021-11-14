import tests.route_helpers as rh
import pytest, time
@pytest.fixture
def clear():
    return rh.clear()

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()['token']

@pytest.fixture
def create_channel(clear_and_register):
    return rh.channels_create(clear_and_register, "channel", True).json()["channel_id"]

@pytest.fixture
def first_user_data():
    response = rh.auth_register("email1@email.com", "password", "userOne", "lastOne")
    return response.json()  

@pytest.fixture
def second_user_data():
    response = rh.auth_register("email2@email.com", "password", "userTwo", "lastTwo")
    return response.json()  


@pytest.fixture
def create_dm(clear_and_register):
    return rh.dm_create(clear_and_register, []).json()["dm_id"]

# Valid inputs

# Metrics when first user registers and does not join dm or channel
def test_user_stats_register_user(clear_and_register):
    user_1 = rh.user_stats(clear_and_register).json()["user_stats"]
    assert len(user_1["channels_joined"]) == 1
    assert user_1["channels_joined"][-1]["num_channels_joined"] == 0
    assert type(user_1["involvement_rate"]) is float

# Metrics for channels and dms work
def test_user_stats_join_channel_dm(clear_and_register, create_channel, create_dm):
    user = rh.user_stats(clear_and_register).json()["user_stats"]
  
    assert len(user["channels_joined"]) == 2
    assert user["channels_joined"][-1]["num_channels_joined"] == 1

    assert len(user["dms_joined"]) == 2
    assert user["dms_joined"][-1]["num_dms_joined"] == 1

    assert len(user["messages_sent"]) == 1
    
    assert user["involvement_rate"] == 1
    assert type(user["involvement_rate"]) is float

# Metrics for messages works
def test_user_stats_messages_metrics(clear, first_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]
    rh.message_send(first_user_data["token"], channel_1, "hello")
    time_message_1 = time.time()
    rh.message_send(first_user_data["token"], channel_1, "hello")
    time_message_2 = time.time()
    rh.message_send(first_user_data["token"], channel_1, "hello")
    time_message_3 = time.time()
    rh.message_send(first_user_data["token"], channel_1, "hello")
    time_message_4 = time.time()

    user = rh.user_stats(first_user_data["token"]).json()["user_stats"]
    # seperate time stamp for each message sent
    assert len(user["messages_sent"]) == 5

    assert user["messages_sent"][0]["num_messages_sent"] == 0
    assert user["messages_sent"][1]["num_messages_sent"] == 1
    assert user["messages_sent"][2]["num_messages_sent"] == 2
    assert user["messages_sent"][3]["num_messages_sent"] == 3
    assert user["messages_sent"][4]["num_messages_sent"] == 4

    assert abs(user["messages_sent"][1]["time_stamp"] - time_message_1) < 2
    assert abs(user["messages_sent"][2]["time_stamp"] - time_message_2) < 2
    assert abs(user["messages_sent"][3]["time_stamp"] - time_message_3) < 2
    assert abs(user["messages_sent"][4]["time_stamp"] - time_message_4) < 2
    
    assert user["involvement_rate"] == 1

# involvement rate changes correctly
def test_user_stats_involvement_rate_change(clear, first_user_data, second_user_data):
    assert rh.user_stats(first_user_data["token"]).json()["user_stats"]["involvement_rate"] == 0
    rh.channels_create(second_user_data["token"], "channel_1", True)
    assert rh.user_stats(second_user_data["token"]).json()["user_stats"]["involvement_rate"] == 1
    rh.channels_create(first_user_data["token"], "channel_2", True)
    assert rh.user_stats(first_user_data["token"]).json()["user_stats"]["involvement_rate"] == 0.5

def test_user_stats_messages_from_multiple_users(clear, first_user_data, second_user_data):
    response = rh.channels_create(first_user_data["token"], "channel_1", True)
    channel_1 = response.json()["channel_id"]
    rh.message_send(first_user_data["token"], channel_1, "hello")

    user = rh.user_stats(first_user_data["token"]).json()["user_stats"]
    assert user["messages_sent"][-1]["num_messages_sent"] == 1

    rh.channel_join(second_user_data["token"], channel_1)
    rh.message_send(second_user_data["token"], channel_1, "hello")

    user = rh.user_stats(first_user_data["token"]).json()["user_stats"]
    assert user["messages_sent"][-1]["num_messages_sent"] == 1

# Number of messages and dms decrease if they are removed
def test_user_stats_num_dms_messages_decrease(clear_and_register, create_dm, create_channel):
    rh.message_senddm(clear_and_register, create_dm, "hello")
    rh.message_senddm(clear_and_register, create_dm, "hello")
    rh.message_senddm(clear_and_register, create_dm, "hello")

    og_msg = rh.message_send(clear_and_register, create_channel, "hello").json()["message_id"]
    removing_message_id = rh.message_send(clear_and_register, create_channel, "hello").json()["message_id"]

    user = rh.user_stats(clear_and_register).json()["user_stats"]
    assert user["dms_joined"][-1]["num_dms_joined"] == 1
    assert user["messages_sent"][-1]["num_messages_sent"] == 5

    rh.dm_remove(clear_and_register, create_dm)
    rh.message_remove(clear_and_register, removing_message_id)
    rh.message_edit(clear_and_register, og_msg, "bye")
    rh.message_share(clear_and_register, og_msg, "hello", create_channel, -1)
    print(rh.user_stats(clear_and_register).json()["user_stats"])
    user = rh.user_stats(clear_and_register).json()["user_stats"]
    assert user["dms_joined"][-1]["num_dms_joined"] == 0
    assert user["messages_sent"][-1]["num_messages_sent"] == 6



# user changes only when messages are sent
def test_user_stats_with_delayed_messages(clear_and_register, create_channel, create_dm):
    # Send a message in the dm and channel in three seconds
    rh.message_sendlater(clear_and_register, create_channel, "hello", int(time.time()) + 2)
    rh.message_sendlaterdm(clear_and_register, create_dm, "hello", int(time.time()) + 2)
    assert len(rh.user_stats(clear_and_register).json()["user_stats"]["messages_sent"]) == 1
    assert rh.user_stats(clear_and_register).json()["user_stats"]["messages_sent"][-1]["num_messages_sent"] == 0
    time.sleep(2)
    print(rh.user_stats(clear_and_register).json()["user_stats"])
    assert len(rh.user_stats(clear_and_register).json()["user_stats"]["messages_sent"]) == 3
    assert rh.user_stats(clear_and_register).json()["user_stats"]["messages_sent"][-1]["num_messages_sent"] == 2

# Invalid inputs

# Invalid token
def test_user_stats_invalid_token(clear_and_register):
    assert rh.user_stats(clear_and_register + 'invalidtoken').status_code == 403

# Invalid session
def test_user_stats_invalid_session(clear_and_register):
    rh.auth_logout(clear_and_register)
    assert rh.user_stats(clear_and_register).status_code == 403

