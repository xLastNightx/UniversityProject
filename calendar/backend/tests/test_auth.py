import pytest
from app import auth_utils

def test_register_user():
    auth_utils.register_user("test@test.com", "password123", "Test User")
    user = auth_utils.get_user("test@test.com")
    assert user is not None
    assert user["name"] == "Test User"

def test_authenticate_user():
    assert auth_utils.authenticate_user("test@test.com", "password123") == True
    assert auth_utils.authenticate_user("test@test.com", "wrongpass") == False

def test_change_password():
    auth_utils.change_password("test@test.com", "password123", "newpass456")
    assert auth_utils.authenticate_user("test@test.com", "newpass456") == True