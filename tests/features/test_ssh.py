import pytest
from ax_devil_device_api.features.ssh import SSHClient, SSHUser

@pytest.mark.integration
def test_add_user(client):
    """Test adding a new SSH user."""
    result = client.ssh.add_user("testuser", "testpass", "Test User")
    assert result.is_success
    assert isinstance(result.data, SSHUser)
    assert result.data.username == "testuser"
    assert result.data.comment == "Test User"

@pytest.mark.unit
def test_add_user_invalid_input(client):
    """Test adding user with invalid input."""
    result = client.ssh.add_user("", "testpass")
    assert not result.is_success
    assert result.error.code == "username_password_required"

@pytest.mark.integration
def test_get_users(client):
    """Test retrieving all SSH users."""
    # Add a test user first
    client.ssh.add_user("testuser", "testpass")
    
    result = client.ssh.get_users()
    assert result.is_success
    assert isinstance(result.data, list)
    assert all(isinstance(user, SSHUser) for user in result.data)
    assert any(user.username == "testuser" for user in result.data)

@pytest.mark.integration
def test_get_user(client):
    """Test retrieving a specific SSH user."""
    # Add a test user first
    client.ssh.add_user("testuser", "testpass", "Test User")
    
    result = client.ssh.get_user("testuser")
    assert result.is_success
    assert isinstance(result.data, SSHUser)
    assert result.data.username == "testuser"
    assert result.data.comment == "Test User"

@pytest.mark.unit
def test_get_user_invalid_input(client):
    """Test retrieving user with invalid input."""
    result = client.ssh.get_user("")
    assert not result.is_success
    assert result.error.code == "username_required"

@pytest.mark.integration
def test_modify_user(client):
    """Test modifying an SSH user."""
    # Add a test user first
    client.ssh.add_user("testuser", "testpass")
    
    result = client.ssh.modify_user("testuser", password="newpass", comment="Updated User")
    assert result.is_success
    assert isinstance(result.data, SSHUser)
    assert result.data.username == "testuser"
    assert result.data.comment == "Updated User"

@pytest.mark.unit
def test_modify_user_invalid_input(client):
    """Test modifying user with invalid input."""
    result = client.ssh.modify_user("")
    assert not result.is_success
    assert result.error.code == "username_required"

@pytest.mark.integration
def test_remove_user(client):
    """Test removing an SSH user."""
    # Add a test user first
    client.ssh.add_user("testuser", "testpass")
    
    result = client.ssh.remove_user("testuser")
    assert result.is_success
    
    # Verify user is removed
    result = client.ssh.get_user("testuser")
    assert not result.is_success

@pytest.mark.unit
def test_remove_user_invalid_input(client):
    """Test removing user with invalid input."""
    result = client.ssh.remove_user("")
    assert not result.is_success
    assert result.error.code == "username_required"