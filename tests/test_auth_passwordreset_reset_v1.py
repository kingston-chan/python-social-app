import tests.route_helpers as rh
import pytest, mailslurp_client, re

# Set up testing with mailslurp_client
configuration = mailslurp_client.Configuration()
configuration.api_key['x-api-key'] = "5276619eb3cc8ca6e2c3e939f7bd0ce24526562d8bb0b7fa9a1b6c1a63ecd911"

@pytest.fixture
def clear_and_register():
    rh.clear()
    rh.auth_register("random@gmail.com", "123abc!@#", "John", "Smith")

@pytest.fixture
def reset_password():
    rh.auth_passwordreset_request("random@gmail.com")

def test_use_reset_code(clear_and_register):
    with mailslurp_client.ApiClient(configuration) as api_client:
        # Create an inbox to recieve reset code
        inbox_controller = mailslurp_client.InboxControllerApi(api_client)
        inbox_1 = inbox_controller.get_inbox("610896f4-673b-4df3-be1a-2c1ac465abdc")

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
        sent_email_body = re.compile("Code for password reset for Streams: ([a-zA-Z0-9]{6})")
        code = sent_email_body.match(email.body).group(1)

        # Use code to reset password
        assert rh.auth_passwordreset_reset(code, "password2").status_code == 200

        # Logs in successfully with new password
        assert rh.auth_login(inbox_1.email_address, "password2").status_code == 200


def test_invalid_reset_code(clear_and_register, reset_password):
    assert rh.auth_passwordreset_reset("invalidresetcode", "validpassword").status_code == 400

def test_invalid_password(clear_and_register, reset_password):
    assert rh.auth_passwordreset_reset("resetcode", "pass").status_code == 400