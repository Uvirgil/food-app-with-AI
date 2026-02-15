from auth import authenticate, create_account


class AuthManager:
    def login(self, username: str, password: str):
        # Daca lipseste username sau parola, intoarcem None (login esuat)
        if not username or not password:
            return None

        # Apelam functia authenticate din modulul auth
        return authenticate(username, password)

    def register(self, username: str, password: str) -> bool:
        # Daca lipseste username sau parola, nu putem crea cont
        if not username or not password:
            return False

        # Apelam functia create_account din modulul auth
        return create_account(username, password)