# Nombre raiz de las colas creadas para el proyecto
QUEUE_ROOT = "2311-01"

# Colas usadas en el proyecto
queue_clientes =  f"{QUEUE_ROOT}_clientes"
queue_robots =  f"{QUEUE_ROOT}_clientes"
queue_repartidores =  f"{QUEUE_ROOT}_clientes"

# Servidor de colas
host_queues = "redes2.ii.uam.es"

# Probabilidades
p_almacen = 0.9
p_entrega = 0.9