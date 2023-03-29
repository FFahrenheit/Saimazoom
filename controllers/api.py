from controllers.database import Database
from utils.order_status import OrderStatus
from models.user import User
from models.order import Order

class API:
    def __init__(self) -> None:
        self.db = Database()

    def crear_orden(self, body: dict) -> int:
        orden = Order()
        orden.from_dict(body)

        return self.db.insert_record(
            "INSERT INTO orders(status, description, total, client) VALUES (?, ?, ?, ?)",
            (OrderStatus.CREATED.value, orden.description, orden.total, orden.client))
    
    def registrar_usuario(self, body: dict) -> bool:
        usuario = User(from_dict=body)

        return self.db.insert_record(
            "INSERT INTO user(name, username, password) VALUES (?, ?, ?)", 
            (usuario.name, usuario.username, usuario.password))
    
    def login(self, user: str, password: str) -> User:
        return self.db.get_first(
            "SELECT * FROM user WHERE username = ? AND password = ?",
            (user, password))
    
    def obtener_ordenes(self, client: str):
        return self.db.get_select(
            "SELECT * FROM orders WHERE client = ? ORDER BY id ASC",
            (client,))
    
    def actualizar_orden(self, order_id, status):
        return self.db.update_record(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id)
        )
    
    def obtener_orden(self, order_id):
        order = self.db.get_first(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,))
        
        events = self.db.get_select(
            "SELECT * FROM log WHERE order_id = ?",
            (order_id,))
        
        order['events'] = events

        return order
