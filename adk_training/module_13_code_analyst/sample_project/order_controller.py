"""
Sample project - REST API endpoints
Służy do testowania Code RAG w module_13
"""


class OrderController:
    """REST kontroler dla zamówień."""

    def __init__(self, order_service, auth_service):
        self.order_service = order_service
        self.auth_service = auth_service

    def create_order(self, request) -> dict:
        """
        POST /api/orders
        Tworzy nowe zamówienie. Wymaga autoryzacji.

        Body: {
            "items": [{"product_id": 1, "quantity": 2}],
            "shipping_address": "ul. Przykładowa 1, Warszawa"
        }
        """
        user_id = self._authenticate(request)
        if not self.auth_service.check_permission(user_id, "orders", "write"):
            return {"error": "Brak uprawnień", "status": 403}

        items = request.body.get("items", [])
        if not items:
            return {"error": "Zamówienie musi zawierać przynajmniej jeden produkt", "status": 400}

        order = self.order_service.create(
            user_id=user_id,
            items=items,
            shipping_address=request.body.get("shipping_address"),
        )
        return {"data": order, "status": 201}

    def get_order(self, request, order_id: int) -> dict:
        """
        GET /api/orders/{order_id}
        Pobiera szczegóły zamówienia.
        """
        user_id = self._authenticate(request)
        order = self.order_service.get(order_id)

        if not order:
            return {"error": "Zamówienie nie znalezione", "status": 404}

        # Użytkownik widzi tylko swoje zamówienia, admin - wszystkie
        if order["user_id"] != user_id:
            if not self.auth_service.check_permission(user_id, "orders", "read_all"):
                return {"error": "Brak dostępu", "status": 403}

        return {"data": order, "status": 200}

    def list_orders(self, request) -> dict:
        """
        GET /api/orders?status=pending&page=1
        Lista zamówień użytkownika z filtrowaniem i paginacją.
        """
        user_id = self._authenticate(request)
        status_filter = request.params.get("status")
        page = int(request.params.get("page", 1))

        orders = self.order_service.list_by_user(
            user_id=user_id,
            status=status_filter,
            page=page,
        )
        return {"data": orders, "status": 200}

    def cancel_order(self, request, order_id: int) -> dict:
        """
        DELETE /api/orders/{order_id}
        Anuluje zamówienie (jeśli status pozwala).
        """
        user_id = self._authenticate(request)
        order = self.order_service.get(order_id)

        if not order:
            return {"error": "Zamówienie nie znalezione", "status": 404}
        if order["user_id"] != user_id:
            return {"error": "Brak dostępu", "status": 403}
        if order["status"] not in ("pending", "confirmed"):
            return {"error": "Nie można anulować zamówienia w statusie: " + order["status"], "status": 400}

        self.order_service.cancel(order_id)
        return {"message": "Zamówienie anulowane", "status": 200}

    def _authenticate(self, request) -> int:
        """Wyciąga user_id z tokena autoryzacji."""
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise PermissionError("Brak tokena autoryzacji")
        session = self.auth_service.validate_token(token)
        return session["user_id"]
