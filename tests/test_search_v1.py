import tests.route_helpers as rh
import pytest, time

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()['token']

# Valid inputs

def test_correct_messages(clear_and_register):
    channel1 = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    channel2 = rh.channels_create(clear_and_register, "channel2", True).json()["channel_id"]
    dm1 = rh.dm_create(clear_and_register, []).json()["dm_id"]
    dm2 = rh.dm_create(clear_and_register, []).json()["dm_id"]

    msg_check1 = rh.message_send(clear_and_register, channel1, "hello channel1").json()["message_id"]
    rh.message_send(clear_and_register, channel1, "bye")
    msg_check2 = rh.message_send(clear_and_register, channel2, "channel2hello").json()["message_id"]
    rh.message_send(clear_and_register, channel2, "bye")
    msg_check3 = rh.message_senddm(clear_and_register, dm1, "hello dm1").json()["message_id"]
    rh.message_senddm(clear_and_register, dm1, "bye")
    msg_check4 = rh.message_senddm(clear_and_register, dm2, "dm2hello").json()["message_id"]
    rh.message_senddm(clear_and_register, dm2, "bye")

    messages = rh.search(clear_and_register, "hello").json()["messages"]

    uid = rh.auth_login("random@gmail.com", "123abc!@#").json()["auth_user_id"]

    assert len(messages) == 4
    
    assert messages[0]["message_id"] == msg_check1
    assert messages[0]["message"] == "hello channel1"
    assert messages[0]["u_id"] == uid
    assert "time_created" in messages[0]
    assert "reacts" in messages[0]
    assert "is_pinned" in messages[0]

    assert messages[1]["message_id"] == msg_check2
    assert messages[1]["message"] == "channel2hello"
    assert messages[1]["u_id"] == uid
    assert "time_created" in messages[1]
    assert "reacts" in messages[1]
    assert "is_pinned" in messages[1]

    assert messages[2]["message_id"] == msg_check3
    assert messages[2]["message"] == "hello dm1"
    assert messages[2]["u_id"] == uid
    assert "time_created" in messages[2]
    assert "reacts" in messages[2]
    assert "is_pinned" in messages[2]

    assert messages[3]["message_id"] == msg_check4
    assert messages[3]["message"] == "dm2hello"
    assert messages[3]["u_id"] == uid
    assert "time_created" in messages[3]
    assert "reacts" in messages[3]
    assert "is_pinned" in messages[3]

# Search for not yet sent messages produces no results
def test_sendlater_and_dm(clear_and_register):
    channel1 = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    dm1 = rh.dm_create(clear_and_register, []).json()["dm_id"]

    msg1 = rh.message_sendlater(clear_and_register, channel1, "hellohellohello", int(time.time()) + 2).json()["message_id"]
    msg2 = rh.message_sendlaterdm(clear_and_register, dm1, "hellodm2hello", int(time.time()) + 2).json()["message_id"]

    assert len(rh.search(clear_and_register, "hello").json()["messages"]) == 0

    time.sleep(2)

    messages = rh.search(clear_and_register, "hello").json()["messages"]
    assert len(messages) == 2
    
    assert messages[0]["message_id"] == msg1
    assert messages[0]["message"] == "hellohellohello"

    assert messages[1]["message_id"] == msg2
    assert messages[1]["message"] == "hellodm2hello"

# Invalid inputs

# Invalid query length
def test_invalid_query_length(clear_and_register):
    channel1 = rh.channels_create(clear_and_register, "channel1", True).json()["channel_id"]
    dm1 = rh.dm_create(clear_and_register, []).json()["dm_id"]
    rh.message_send(clear_and_register, channel1, "bye")
    rh.message_senddm(clear_and_register, dm1, "bye")

    assert rh.search(clear_and_register, "").status_code == 400
    assert rh.search(clear_and_register, "a" * 1001).status_code == 400


# Invalid token
def test_invalid_token(clear_and_register):
    assert rh.search(clear_and_register + "invalidtoken", "hello").status_code == 403

# Invalid session
def test_invalid_session(clear_and_register):
    rh.auth_logout(clear_and_register)
    assert rh.search(clear_and_register, "hello").status_code == 403
    