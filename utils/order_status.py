from enum import Enum

class OrderStatus(Enum):
    CREATED = "Orden creada"
    PROCESSING = "Orden en proceso"
    FOUND = "Orden encontrada"
    NOT_FOUND = "Orden no encontrada"
    ON_DELIVER = "Orden en entrega"
    DELIVERED = "Orden entregada"
    LOST = "Orden perdida"
    CANCELLED = "Orden cancelada"