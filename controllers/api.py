from controllers.database import Database
from utils.order_status import OrderStatus
from models.user import User
from models.order import Order

"""
Clase API, usada principalmente para gestionar las consultas
SQL de nuestro modelo de datos
"""
class API:
    def __init__(self) -> None:
        """
        Inicializa nuestra clase con una instancia a la clase
        usada para conectarnos a la BD
        """
        # Crea una instancia de la clase Database y la guarda en el atributo self.db
        self.db = Database()
    
    def crear_orden(self, body: dict) -> int:
        """Inserta un registro de orden basado en sus parametros

        Args:
            body (dict): Diccionario con los parametros de orden

        Returns:
            int: 0 Si no hubo exito, de otra forma el ID generado con la instruccion INSERT
        """
        # Crea una instancia de la clase Order y llama al método from_dict() para cargar los valores del body
        orden = Order()
        orden.from_dict(body)
        # Ejecuta una consulta INSERT en la base de datos para insertar una nueva orden con los valores de Order y el estado CREATED
        return self.db.insert_record(
            "INSERT INTO orders(status, description, total, client) VALUES (?, ?, ?, ?)",
            (OrderStatus.CREATED.value, orden.description, orden.total, orden.client))
    
    def registrar_usuario(self, body: dict) -> bool:
        """Registra un usuario en la BD

        Args:
            body (dict): Diccionario con los datos del usuario en formato clave - valor

        Returns:
            bool: Si hubo exito en el registro
        """
        # Crea una instancia de la clase User 
        usuario = User(from_dict=body)
        # Ejecuta una consulta INSERT en la base de datos para insertar un nuevo usuario con los valores de User
        return self.db.insert_record(
            "INSERT INTO user(name, username, password) VALUES (?, ?, ?)", 
            (usuario.name, usuario.username, usuario.password))

    def login(self, user: str, password: str) -> User:
        """Intenta hacer login con el usuario y contraseña enviados

        Args:
            user (str): nombre de usuario
            password (str): contraseña enviada

        Returns:
            User: Si hubo exito, un objeto Usuario, en otro caso None
        """
        # Ejecuta una consulta SELECT para obtener el primer usuario que tenga el mismo nombre de usuario y contraseña que los parámetros recibidos
        return self.db.get_first(
            "SELECT * FROM user WHERE username = ? AND password = ?",
            (user, password))

    def obtener_ordenes(self, client: str) -> list:
        """Obtiene las ordenes de un cliente

        Args:
            client (str): nombre de usuario del cliente en cuestion

        Returns:
            list<dict>: lista de las ordenes obtenidas en formato diccionario
        """
        # Ejecuta una consulta SELECT para obtener todas las órdenes del cliente dado, ordenadas por el id de manera ascendente
        return self.db.get_select(
            "SELECT * FROM orders WHERE client = ? ORDER BY id ASC",
            (client,))
    
    def actualizar_orden(self, order_id: int, status: str) -> bool:
        """Actualiza una orden de estado

        Args:
            order_id (int): ID de la orden
            status (str): Estado a actualizar

        Returns:
            bool : Si hubo exito con el UPDATE 
        """
        # Cambia el status de una orden haciendo una peticion de tipo UPDATE a la base de datos
        return self.db.update_record(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id)
        )
    
    def obtener_orden(self, order_id: int) -> dict:
        """Obtiene los detalles de una orden

        Args:
            order_id (int): ID de la orden

        Returns:
            dict: diccionario con los detalles de la orden y su log de eventos
        """
        # Ejecuta una consulta SELECT en la base de datos para obtener la orden con el id recibido
        order = self.db.get_first(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,))
        
        # Ejecuta una consulta SELECT en la base de datos para obtener todos los eventos asociados a la orden con el id recibido
        events = self.db.get_select(
            "SELECT * FROM log WHERE order_id = ?",
            (order_id,))
        
        # Agrega los eventos obtenidos a la orden como una lista de diccionarios en la clave 'events'
        order['events'] = events

        # Retorna la orden
        return order
