def check_password(password):
    if len(password) < 8 or len(password) > 20:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    if not any(char in "!@#$%^&*()-_+=<>?/|{}[]:;\"'`~" for char in password):
        return False
    return True
def check_username(username):
    if len(username)!=12:
        return False
    if not any(char.isdigit() for char in username):
        return False
    return True
def check_name(name):
    if len(name)<2 or len(name)>5:
        return False
    return True
def check_phone(phone):
    if len(phone)!=11:
        return False
    if not any(char.isdigit() for char in phone):
        return False
    if phone[0]!='1':
        return False
    return True