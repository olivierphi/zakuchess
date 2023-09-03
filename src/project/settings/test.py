from os import environ as env

env["SECRET_KEY"] = "test-secret-key"

from .development import *

# To be efficient password hashers have to be slow by design
# --> let's speed up our password hashing by purposefully opting for a weak algorithm during tests :-)
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
