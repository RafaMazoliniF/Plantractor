import re

def isUsernameValid(username):
    if not username or not isinstance(username, str):
        return False
    
    username = username.strip()
    
    if len(username) < 3 or len(username) > 30:
        return False
    
    if not username.replace('_', '').isalnum():
        return False
    
    if username[0].isdigit():
        return False
    
    return True

def isPasswordValid(password):
    if not password or not isinstance(password, str):
        return False
    
    if len(password) < 6:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'\d', password):
        return False
    
    if not re.search(r'[*&#@$%]', password):
        return False
    
    return True