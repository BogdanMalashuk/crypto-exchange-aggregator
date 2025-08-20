from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

_cipher = Fernet(settings.SECRETS_FERNET_KEY.encode()
                 if isinstance(settings.SECRETS_FERNET_KEY, str)
                 else settings.SECRETS_FERNET_KEY)


def encrypt_text(plain: str) -> str:
    if plain is None:
        return ""
    token = _cipher.encrypt(plain.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_text(token: str) -> str:
    if not token:
        return ""
    try:
        value = _cipher.decrypt(token.encode("utf-8"))
        return value.decode("utf-8")
    except InvalidToken:
        return ""
