import pytest

from ax_devil_device_api.utils.errors import FeatureError

@pytest.mark.unit
def test_add_user_invalid_input(client):
    """Test adding user with invalid input."""
    with pytest.raises(FeatureError) as exc_info:
        client.ssh.add_user("", "testpass")
    assert exc_info.value.code == "username_password_required"

@pytest.mark.integration
def test_get_users(client):
    """Test retrieving all SSH users."""
    # Add a test user first
    client.ssh.add_user("testuser", "testpass")
    
    result = client.ssh.get_users()
    assert isinstance(result, list)
    assert any(user["username"] == "testuser" for user in result)

    # Remove the test user
    client.ssh.remove_user("testuser")

@pytest.mark.integration
def test_get_user(client):
    """Test retrieving a specific SSH user."""
    # Add a test user first
    client.ssh.add_user("testuser", "testpass", "Test User")
    
    result = client.ssh.get_user("testuser")
    assert isinstance(result, dict)
    assert result["username"] == "testuser"
    assert result["comment"] == "Test User"

    # Remove the test user
    client.ssh.remove_user("testuser")

@pytest.mark.unit
def test_get_user_invalid_input(client):
    """Test retrieving user with invalid input."""
    with pytest.raises(FeatureError) as exc_info:
        client.ssh.get_user("")
    assert exc_info.value.code == "username_required"

@pytest.mark.integration
def test_user_lifecycle(client):
    """Test the full lifecycle of an SSH user - add, modify and remove."""
    client.ssh.add_user("testuser", "testpass")
    
    client.ssh.modify_user("testuser", password="newpass", comment="Updated User")
    
    client.ssh.remove_user("testuser")
    
    with pytest.raises(FeatureError) as exc_info:
        client.ssh.get_user("testuser")
    assert exc_info.value.code == "get_user_error"

@pytest.mark.unit
def test_modify_user_invalid_input(client):
    """Test modifying user with invalid input."""
    with pytest.raises(FeatureError) as exc_info:
        client.ssh.modify_user("", password="newpass", comment="Updated User")
    assert exc_info.value.code == "username_required"

@pytest.mark.unit
def test_remove_user_invalid_input(client):
    """Test removing user with invalid input."""
    with pytest.raises(FeatureError) as exc_info:
        client.ssh.remove_user("")
    assert exc_info.value.code == "username_required"