import json
import os
import hashlib

# Fisierul unde sunt salvati utilizatorii
USERS_FILE = "users.json"


def load_users():
    # Daca fisierul nu exista, intoarcem un dictionar gol
    if not os.path.exists(USERS_FILE):
        return {}

    # Citim fisierul JSON si returnam continutul ca dictionar
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    # Salvam dictionarul de utilizatori inapoi in fisier
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def hash_password(password):
    # Criptam parola folosind SHA-256 pentru securitate
    return hashlib.sha256(password.encode()).hexdigest()


def create_account(username, password):
    # Incarcam utilizatorii existenti
    users = load_users()

    # Daca username-ul exista deja, nu permitem crearea contului
    if username in users:
        return False  # user already exists

    # Salvam parola criptata
    users[username] = {
        "password_hash": hash_password(password)
    }

    # Scriem modificarile in fisier
    save_users(users)
    return True


def authenticate(username, password):
    # Incarcam utilizatorii existenti
    users = load_users()

    # Daca username-ul nu exista, login esuat
    if username not in users:
        return None

    # Verificam daca parola introdusa corespunde hash-ului salvat
    if users[username]["password_hash"] == hash_password(password):
        return username  # login OK

    # Parola incorecta
    return None