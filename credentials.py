import keyring
import json
import getpass

def set_credentials():
    ic_user = input("Enter your IC username: ")
    keyring.set_password("macbook_checkin", "ic_user", ic_user)
    ic_pw = getpass.getpass("Enter your IC password: ")
    keyring.set_password("macbook_checkin", "ic_pw", ic_pw)
    destiny_user = input("Enter your destiny username: ")
    keyring.set_password("macbook_checkin", "destiny_user", destiny_user)
    destiny_pw = getpass.getpass("Enter your destiny password: ")
    keyring.set_password("macbook_checkin", "destiny_pw", destiny_pw)
    checkin_email = input("Enter the full email address for MacBook check-in: ")
    keyring.set_password("macbook_checkin", "checkin_email", checkin_email)
    checkin_email_pw = getpass.getpass("Enter your the email password: ")
    keyring.set_password("macbook_checkin", "checkin_email_pw", checkin_email_pw)
    
    userCredentials = {
        "ic_user": ic_user,
        "ic_pw": ic_pw,
        "destiny_user": destiny_user,
        "destiny_pw": destiny_pw,
        "checkin_email": checkin_email,
        "checkin_email_pw": checkin_email_pw
    }
    return(userCredentials)

def get_credentials():
    ic_user = keyring.get_password("macbook_checkin", "ic_user")
    ic_pw = keyring.get_password("macbook_checkin", "ic_pw")
    destiny_user = keyring.get_password("macbook_checkin", "destiny_user")
    destiny_pw = keyring.get_password("macbook_checkin", "destiny_pw")
    checkin_email = keyring.get_password("macbook_checkin", "checkin_email")
    checkin_email_pw = keyring.get_password("macbook_checkin", "checkin_email_pw")
    userCredentials = {
        "ic_user": ic_user,
        "ic_pw": ic_pw,
        "destiny_user": destiny_user,
        "destiny_pw": destiny_pw,
        "checkin_email": checkin_email,
        "checkin_email_pw": checkin_email_pw
    }
    if not all(userCredentials.values()):
        raise ValueError("Incomplete userCredentials, please run with --reset-credentials arg")
    return(userCredentials)

def get_user_info():
    try:
        userCredentials = get_credentials()
    except ValueError:
        userCredentials = set_credentials()

    return(userCredentials)