from unittest.mock import Mock

import pytest

from src.ax_devil_device_api.core.config import Protocol
from src.ax_devil_device_api.features.ssh import SSHClient
from src.ax_devil_device_api.utils.errors import FeatureError


def response(payload, status=200):
    """Create a minimal response double for SSH contract tests."""
    result = Mock(status_code=status)
    result.json.return_value = payload
    return result


def discovery_response(rest_api="/config/rest/ssh/v1", state="released"):
    """Create a discovery response containing one SSH API version."""
    return response(
        {
            "framework_version": "1.0.0",
            "apis": {
                "ssh": {
                    "v1": {
                        "state": state,
                        "version": "1.0.0" if state == "released" else "1.0.0-beta.1",
                        "rest_api": rest_api,
                    }
                }
            },
        }
    )


def ssh_device(*responses, protocol=Protocol.HTTPS):
    """Create a transport double with a configured protocol."""
    device = Mock()
    device.config.protocol = protocol
    device.request.side_effect = responses
    return device


@pytest.mark.unit
def test_add_user_discovers_released_api_and_sends_official_payload():
    device = ssh_device(discovery_response(), response({"status": "success"}))

    assert SSHClient(device).add_user("testuser", "testpass") is None

    discovery_call, add_call = device.request.call_args_list
    discovery_endpoint = discovery_call.args[0]
    add_endpoint = add_call.args[0]
    assert (discovery_endpoint.method, discovery_endpoint.path) == (
        "GET",
        "/config/discover",
    )
    assert (add_endpoint.method, add_endpoint.path) == (
        "POST",
        "/config/rest/ssh/v1/users",
    )
    assert add_call.kwargs["json"] == {
        "data": {"username": "testuser", "password": "testpass"}
    }


@pytest.mark.unit
def test_ssh_endpoint_is_cached_and_comment_is_sent_when_nonempty():
    device = ssh_device(
        discovery_response(),
        response({"status": "success", "data": []}),
        response({"status": "success", "data": {"username": "a/b"}}),
    )
    client = SSHClient(device)

    assert client.get_users() == []
    assert client.get_user("a/b") == {"username": "a/b"}

    assert device.request.call_count == 3
    item_endpoint = device.request.call_args_list[2].args[0]
    assert item_endpoint.path == "/config/rest/ssh/v1/users/a%2Fb"

    device = ssh_device(discovery_response(), response({"status": "success"}))
    SSHClient(device).add_user("testuser", "testpass", "Service account")
    assert device.request.call_args.kwargs["json"] == {
        "data": {
            "username": "testuser",
            "password": "testpass",
            "comment": "Service account",
        }
    }


@pytest.mark.unit
def test_modify_and_remove_use_item_operations_and_return_none():
    device = ssh_device(
        discovery_response(),
        response({"status": "success"}),
        response({"status": "success"}),
    )
    client = SSHClient(device)

    assert client.modify_user("user", password="newpass", comment="Updated") is None
    assert client.remove_user("user") is None

    patch_call = device.request.call_args_list[1]
    assert (patch_call.args[0].method, patch_call.args[0].path) == (
        "PATCH",
        "/config/rest/ssh/v1/users/user",
    )
    assert patch_call.kwargs["json"] == {
        "data": {"password": "newpass", "comment": "Updated"}
    }
    delete_call = device.request.call_args_list[2]
    assert (delete_call.args[0].method, delete_call.args[0].path) == (
        "DELETE",
        "/config/rest/ssh/v1/users/user",
    )


@pytest.mark.unit
def test_ssh_rejects_http_before_discovery_or_request():
    device = ssh_device(protocol=Protocol.HTTP)

    with pytest.raises(FeatureError, match="requires an HTTPS"):
        SSHClient(device).get_users()

    device.request.assert_not_called()


@pytest.mark.unit
def test_ssh_does_not_select_beta_api():
    device = ssh_device(discovery_response(state="beta"))

    with pytest.raises(FeatureError, match="no released version"):
        SSHClient(device).get_users()

    assert device.request.call_count == 1


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["get_users", "get_user"])
def test_reads_require_typed_data(operation):
    payload = (
        {"status": "success", "data": {}}
        if operation == "get_users"
        else {"status": "success", "data": []}
    )
    device = ssh_device(discovery_response(), response(payload))

    with pytest.raises(FeatureError, match="data"):
        if operation == "get_user":
            SSHClient(device).get_user("user")
        else:
            SSHClient(device).get_users()


@pytest.mark.unit
def test_http_error_and_http_200_error_preserve_error_object():
    error = {"code": "forbidden", "message": "Not allowed", "details": {"x": 1}}
    for status in (403, 200):
        device = ssh_device(
            discovery_response(),
            response({"status": "error", "error": error}, status),
        )

        with pytest.raises(FeatureError) as exc_info:
            SSHClient(device).get_users()

        assert exc_info.value.code == "forbidden"
        assert exc_info.value.message == "Not allowed"
        assert exc_info.value.details == error


@pytest.mark.unit
@pytest.mark.parametrize(
    "payload",
    [None, [], {"status": "success"}, {"status": "error", "error": "bad"}],
)
def test_malformed_ssh_responses_are_rejected(payload):
    response_double = response(payload)
    if payload is None:
        response_double.json.side_effect = ValueError("bad json")
    device = ssh_device(discovery_response(), response_double)

    with pytest.raises(FeatureError):
        SSHClient(device).get_users()


@pytest.mark.unit
def test_add_user_invalid_input():
    device = ssh_device()

    with pytest.raises(FeatureError) as exc_info:
        SSHClient(device).add_user("", "testpass")
    assert exc_info.value.code == "username_password_required"


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["add", "modify"])
def test_explicit_empty_comment_is_rejected_before_request(operation):
    device = ssh_device()
    client = SSHClient(device)

    with pytest.raises(FeatureError) as exc_info:
        if operation == "add":
            client.add_user("user", "password", comment="")
        else:
            client.modify_user("user", password="new-password", comment="")

    assert exc_info.value.code == "comment_required"
    assert exc_info.value.message == "Comment must not be empty"
    device.request.assert_not_called()


@pytest.mark.unit
def test_get_user_invalid_input():
    device = ssh_device()

    with pytest.raises(FeatureError) as exc_info:
        SSHClient(device).get_user("")
    assert exc_info.value.code == "username_required"


@pytest.mark.unit
def test_modify_user_invalid_input():
    device = ssh_device()

    with pytest.raises(FeatureError) as exc_info:
        SSHClient(device).modify_user("", password="newpass", comment="Updated User")
    assert exc_info.value.code == "username_required"


@pytest.mark.unit
def test_remove_user_invalid_input():
    device = ssh_device()

    with pytest.raises(FeatureError) as exc_info:
        SSHClient(device).remove_user("")
    assert exc_info.value.code == "username_required"


@pytest.mark.integration
def test_get_users(client):
    """Test retrieving all SSH users."""
    client.ssh.add_user("testuser", "testpass")
    result = client.ssh.get_users()
    assert isinstance(result, list)
    assert any(user["username"] == "testuser" for user in result)
    client.ssh.remove_user("testuser")


@pytest.mark.integration
def test_get_user(client):
    """Test retrieving a specific SSH user."""
    client.ssh.add_user("testuser", "testpass", "Test User")
    result = client.ssh.get_user("testuser")
    assert isinstance(result, dict)
    assert result["username"] == "testuser"
    assert result["comment"] == "Test User"
    client.ssh.remove_user("testuser")


@pytest.mark.integration
def test_user_lifecycle(client):
    """Test the full lifecycle of an SSH user - add, modify and remove."""
    client.ssh.add_user("testuser", "testpass")
    client.ssh.modify_user("testuser", password="newpass", comment="Updated User")
    client.ssh.remove_user("testuser")
    with pytest.raises(FeatureError) as exc_info:
        client.ssh.get_user("testuser")
    assert isinstance(exc_info.value, FeatureError)
    assert exc_info.value.details["code"] == exc_info.value.code
    assert exc_info.value.details["message"] == exc_info.value.message
