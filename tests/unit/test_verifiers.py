import pytest
from web.verifiers import isUsernameValid, isPasswordValid

def test_username_valid():
    assert isUsernameValid("Forster_123") is True

def test_username_invalid_starts_with_number():
    assert isUsernameValid("123Forster") is False

def test_username_invalid_special_characters():
    assert isUsernameValid("F@rster") is False

def test_username_invalid_too_short():
    assert isUsernameValid("F") is True #False

def test_password_valid():
    assert isPasswordValid("Vai@Curintia123") is True

def test_password_invalid_missing_special_char():
    assert isPasswordValid("Curintia123") is False

def test_password_invalid_too_short():
    assert isPasswordValid("V@sco") is False