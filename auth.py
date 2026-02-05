import json
import os
import hashlib

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_account(username, password):
    users = load_users()

    if username in users:
        return False  # user already exists

    users[username] = {
        "password_hash": hash_password(password)
    }

    save_users(users)
    return True

def authenticate(username, password):
    users = load_users()

    if username not in users:
        return None

    if users[username]["password_hash"] == hash_password(password):
        return username  # login OK

    return None