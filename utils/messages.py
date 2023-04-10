"""
Enums para los mensajes y estados de los mismos
"""
from enum import Enum

#lista de mensajes
class Message(Enum):
    REGISTRO = "RegistroCliente"
    LOGIN = "LoginCliente"
    CREATE_ORDER = "BlueMonday-NewOrder"
    SEARCH_ORDER = "BuscarPedido"
    VIEW_ORDERS = "VerPedidos"
    DELIVER_ORDER = "EntregarPedido"
    CANCEL_ORDER = "MessageOfDeath"
    ORDER_FOUND = "OrderFound"
    ORDER_NOT_FOUND = "OrderNotFound"
    ORDER_DELIVERED = "OrderDeliveredOkay"
    ORDER_LOST = "OrderLostInTranslation"
    ORDER_CANCELED = "CanceledOrder"
    VIEW_ORDER = "ViewOrder"
    CLEAR_CANCELATION = "ClearOrderToCancel"
    ON_DELIVER = "OrderOnDelivery"

#lista de codigos de status
class Status(Enum):
    ERROR = "Error"
    OK = "Ok"
    MALFORMED = "Parsing error"