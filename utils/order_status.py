"""
Enums para los estados de cada orden
"""
from enum import Enum

#enumeracion con los diferentes tipos de estados que puede tener una orden
class OrderStatus(Enum):
    CREATED = "Orden creada"
    PROCESSING = "Orden en proceso"
    FOUND = "Orden encontrada"
    NOT_FOUND = "Orden no encontrada"
    ON_DELIVER = "Orden en entrega"
    DELIVERED = "Orden entregada"
    LOST = "Orden perdida"
    CANCELLED = "Orden cancelada"