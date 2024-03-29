# Nombre raiz de las colas creadas para el proyecto
QUEUE_ROOT = "2311-01"

# Colas usadas en el proyecto
queue_clientes =  f"{QUEUE_ROOT}_clientes"
queue_robots =  f"{QUEUE_ROOT}_robots"
queue_respuesta_robots = f"{QUEUE_ROOT}_robots_reply"
queue_repartidores =  f"{QUEUE_ROOT}_repartidores"
queue_respuesta_repartidores = f"{QUEUE_ROOT}_repartidores_reply"

# Servidor de colas
host_queues = "redes2.ii.uam.es"

# Tiempos de espera
wait_robot_min = 5
wait_robot_max = 10
wait_delivery_min = 10
wait_delivery_max = 20

# Probabilidades
p_almacen = 0.9
p_entrega = 0.9

# Base de datos
database_name = "Saimazoom.sqlite3"
db_directory = "db"
db_model = "model.sql"


#launc_client
n_pedidos = 1
n_prods = 2
prod_name = "v"
client_user = "Sddie_Pinn"
client_pswd = "Sddie_Pinn"
client_name = "Sddie_Pinn"
p_cancelar = 0.15
create_frequency = 20