from . import bitwarden


def username() -> str:
    try:
        username: str = bitwarden.username()
        if username:
            return username
    except:
        pass
    return ""


def password() -> str:
    try:
        password: str = bitwarden.password()
        if password:
            return password
    except:
        pass
    return ""
