from django.contrib.auth.hashers import make_password, check_password


def hash_password(password):
    return make_password(password)


def verify_password(password, hash_password):
    return check_password(password, hash_password)