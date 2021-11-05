import tests.route_helpers as rh
import pytest, mailslurp_client, re

# Set up testing with mailslurp_client
configuration = mailslurp_client.Configuration()
configuration.api_key['x-api-key'] = "c9f19de2102ebab1803a52cf6ab6628c615295c9edf6c68b8689b7974a5c2fc1"

@pytest.fixture
def clear_and_register():
    rh.clear()
    return rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith").json()["token"]

# Invalid emails should work for security purposes
def test_invalid_and_valid_email(clear_and_register):
    assert rh.auth_passwordreset_request("random@gmail.com").status_code == 200
    assert rh.auth_passwordreset_request("bademail@gmail.com").status_code == 200
    assert rh.auth_passwordreset_request("bademail").status_code == 200

# If a valid email is given, it will log out any ongoing sessions corresponding to that
# email.
def test_passwordreset_request_logs_out_all_sessions(clear_and_register):
    rh.auth_passwordreset_request("random@gmail.com")
    assert rh.channels_create(clear_and_register, "channel", True).status_code == 403

# Check that the email is sent and the subject and body is correct
def test_email_is_recieved_contents_correct(clear_and_register):
    with mailslurp_client.ApiClient(configuration) as api_client:
        # Create an inbox to recieve reset code
        inbox_controller = mailslurp_client.InboxControllerApi(api_client)
        inbox_1 = inbox_controller.create_inbox()

        # Register with inbox's email
        rh.auth_register(inbox_1.email_address, "password1", "Test", "test")

        # Send reset code
        rh.auth_passwordreset_request(inbox_1.email_address)

        # Recieve email
        waitfor_controller = mailslurp_client.WaitForControllerApi(api_client)
        email = waitfor_controller.wait_for_latest_email(inbox_id=inbox_1.id, timeout=30000, unread_only=True)

        # Test email subject
        assert email.subject == "Password reset for Streams"

        # Extract code from email body
        assert re.match("Code for password reset for Streams: [a-zA-Z0-9]{6}", email.body)
