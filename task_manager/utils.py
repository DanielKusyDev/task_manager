import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import url_for, request

from task_manager import settings


def generate_key():
    password = settings.SECRET_KEY.encode()
    salt = settings.SALT
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt(message):
    key = generate_key()
    message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(message)
    return encrypted_message.decode()


def decrypt(encrypted_message):
    key = generate_key()
    encrypted_message = encrypted_message.encode()
    f = Fernet(key)
    message = f.decrypt(encrypted_message)
    return message.decode()


class Paginator:

    def __init__(self):
        self.page = int(request.args.get("page", 1))
        self.page_size = int(request.args.get("page_size", settings.DEFAULT_PAGE_SIZE))

    def get_paginated_documents(self, mongo_cursor):
        skip_by = self.page_size * (self.page - 1)
        cursor = mongo_cursor.skip(skip_by).limit(self.page_size)
        return cursor

    def get_navigation(self, total):
        reversed_url = url_for(request.endpoint, _external=True)
        nav = {}
        if total > self.page * self.page_size:
            nav["next"] = reversed_url + f"?page={self.page + 1}&page_size={self.page_size}"
        if self.page > 1:
            nav["previous"] = reversed_url + f"?page={self.page - 1}&page_size={self.page_size}"
        return nav
