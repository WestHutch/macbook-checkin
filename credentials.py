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


def write_school_info():
    school = ""
    while school != "h" and school != "m":
        school = input("Enter m for TMS or h for THS: ")

    schoolInfo = {
        "school": school
    }

    with open("schoolinfo.json", "w") as f:
        json.dump(schoolInfo, f, indent=4)
    return(schoolInfo)

def read_school_info():
    with open("schoolinfo.json", "r") as f:
        schoolInfo = json.load(f)
    return(schoolInfo)

def get_user_info():
    try:
        userCredentials = get_credentials()
    except ValueError:
        userCredentials = set_credentials()

    try:
        schoolInfo = read_school_info()
    except (FileNotFoundError, json.JSONDecodeError):
        schoolInfo = write_school_info()

    userDict = userCredentials | schoolInfo

    return(userDict)