"""
Sample project - Serwis autoryzacji JWT
Służy do testowania Code RAG w module_13
"""

import hashlib
import secrets
from datetime import datetime, timedelta


class AuthService:
    """Serwis uwierzytelniania i autoryzacji."""

    TOKEN_EXPIRY_HOURS = 24
    MAX_LOGIN_ATTEMPTS = 5

    def __init__(self, db_connection, secret_key: str):
        self.db = db_connection
        self.secret_key = secret_key

    def hash_password(self, password: str) -> str:
        """Hashuje hasło z użyciem SHA-256 + salt."""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return f"{salt}:{hashed}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Weryfikuje hasło z przechowywanym hashem."""
        salt, expected_hash = stored_hash.split(":")
        actual_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return actual_hash == expected_hash

    def login(self, username: str, password: str) -> dict:
        """
        Logowanie użytkownika.
        Zwraca token JWT lub error przy nieprawidłowych danych.
        Blokuje konto po 5 nieudanych próbach.
        """
        user = self.db.find_one("users", {"username": username})
        if not user:
            raise ValueError("Użytkownik nie istnieje")

        if user.get("login_attempts", 0) >= self.MAX_LOGIN_ATTEMPTS:
            raise PermissionError("Konto zablokowane - zbyt wiele prób logowania")

        if not self.verify_password(password, user["password_hash"]):
            self.db.update(
                "users",
                {"username": username},
                {"login_attempts": user.get("login_attempts", 0) + 1},
            )
            raise ValueError("Nieprawidłowe hasło")

        # Reset licznika po udanym logowaniu
        self.db.update(
            "users",
            {"username": username},
            {"login_attempts": 0, "last_login": datetime.utcnow()},
        )

        token = self._generate_token(user)
        return {"token": token, "expires_in": self.TOKEN_EXPIRY_HOURS * 3600}

    def _generate_token(self, user: dict) -> str:
        """Generuje token sesji (uproszczony - nie JWT)."""
        payload = f"{user['id']}:{user['role']}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(
            f"{self.secret_key}{payload}".encode()
        ).hexdigest()

    def logout(self, token: str) -> bool:
        """Unieważnia token sesji."""
        return self.db.delete("sessions", {"token": token})

    def check_permission(self, user_id: int, resource: str, action: str) -> bool:
        """Sprawdza czy użytkownik ma uprawnienie do zasobu."""
        user = self.db.find_one("users", {"id": user_id})
        if not user or not user.get("active"):
            return False

        role_permissions = {
            "admin": {"users": ["read", "write", "delete"], "reports": ["read", "write"]},
            "manager": {"users": ["read"], "reports": ["read", "write"]},
            "user": {"reports": ["read"]},
        }

        role = user.get("role", "user")
        allowed = role_permissions.get(role, {}).get(resource, [])
        return action in allowed
