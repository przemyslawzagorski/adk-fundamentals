"""
Sample project - Serwis zarządzania użytkownikami
Służy do testowania Code RAG w module_13
"""


class UserService:
    """Serwis CRUD dla użytkowników."""

    def __init__(self, db_connection):
        self.db = db_connection

    def create_user(self, username: str, email: str, role: str = "user") -> dict:
        """Tworzy nowego użytkownika w systemie."""
        if not username or not email:
            raise ValueError("Username i email są wymagane")
        if "@" not in email:
            raise ValueError("Nieprawidłowy format email")

        user = {
            "username": username,
            "email": email,
            "role": role,
            "active": True,
        }
        user_id = self.db.insert("users", user)
        user["id"] = user_id
        return user

    def get_user(self, user_id: int) -> dict | None:
        """Pobiera użytkownika po ID."""
        return self.db.find_one("users", {"id": user_id})

    def update_user(self, user_id: int, **kwargs) -> dict:
        """Aktualizuje dane użytkownika."""
        allowed_fields = {"email", "role", "active"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            raise ValueError("Brak poprawnych pól do aktualizacji")
        self.db.update("users", {"id": user_id}, updates)
        return self.get_user(user_id)

    def deactivate_user(self, user_id: int) -> bool:
        """Dezaktywuje użytkownika (soft delete)."""
        result = self.db.update("users", {"id": user_id}, {"active": False})
        return result.modified_count > 0

    def list_active_users(self, page: int = 1, per_page: int = 20) -> list:
        """Lista aktywnych użytkowników z paginacją."""
        offset = (page - 1) * per_page
        return self.db.find(
            "users",
            {"active": True},
            limit=per_page,
            offset=offset,
        )
