# 2. Definición del proyecto
El sistema Saimazoom, como conjunto, debe gestionar pedidos, en los que los **clientes** pueden solicitar un producto. Una vez recibido un pedido, el **controlador** debe avisar a un **robot**, que mueve dicho producto del almacén a la cinta transportadora. Una vez en la cinta transportadora, el controlador avisa a un **repartidor**, que lleva el producto a la casa del **cliente**. 
<!-- Las comunicaciones pertinentes entre estos elementos estarán gestionadas por un **controlador** central, que mantiene la comunicación entre los **clientes**, **robots** y **repartidores**. -->

## 2.1. Objetivos y funcionalidad
Los objetivos principales son: 
* La gestión de los pedidos de los **clientes**, que pueden hacer, ver  y cancelar pedidos.
* La gestión de los **robots**, que reciben ordenes de de transportar los productos del almacen a la cinta transportadora.
* La gestión de los **repartidores**, que reparten los productos que hay en la cinta transportadora a la casa de los clientes.
* La gestión del **controlador** central, que tiene que mantener un control de productos, **clientes**, **robots** y **repartidores**. Tiene que guardar también los pedidos, con sus estados, que dependen de la relación con el resto de actores.
* La comunicación entre el **controlador** y el resto de actores

Para cumplir estos objetivos es necesario desarrollar una serie de funcionalidades básicas:
1. Registro de **Cliente**: registro desde una petición de un **Cliente** con un identificador de **cliente** que tiene que ser único.
2. Registro de Pedido: registro en la base de datos del **controlador** central con un id de **cliente** y de producto, también le asigna un estado al pedido.
3. Recepción de pedidos de los **Clientes**: hay que recibir y guardar los pedidos a realizar que están asociados a un **Cliente** y a un producto.
4. Asignación de trabajo a los **Robots**: hay que asignar a los **robots** las tareas de transporte de productos correspondientes a pedidos.
5. Asignación de trabajo a los **Repartidores**: hay que asignar a los **repartidores** las tareas de transporte de productos correspondientes a pedidos.


## 2.2 Requisitos funcionales
1. Un usuario puede registrarse en el sistema proporcionando nombre, nombre de usuario y contraseña
2. Para que un usuario pueda hacer pedidos, deberá de acceder con su nombre de usuario y contraseña
3. Un usuario podrá consultar sus pedidos, mostrando su ID, estado, total y pedidos
4. Un usuario podrá consultar el detalle de un pedido, donde además de los datos del requisito previo, se 5. podrá ver un registro de los cambios de estado en el pedido
5. Un usuario podrá crear pedidos, en donde se le pedirá escribir en texto plano una cantidad “n” de 7. artículos, siendo “n” personalizable por el usuario. 
6. Un usuario podrá crear cualquier cantidad de pedidos
7. Por simplicidad, los pedidos tendrán un coste aleatorio
8. El controlador deberá recibir las peticiones de los usuarios (mediante una cola específica), así como las confirmaciones de robots y repartidores (mediante colas específicas)
9. El controlador, asimismo, tendrá colas para comunicarse con robots y repartidores sin esperar respuesta (de forma asíncrona)
10. El controlador mantendrá toda la información y su estado, tanto de usuarios y pedidos, en una base de datos relacional 
11. El controlador, al recibir una solicitud de pedido, creará dicho pedido y posteriormente enviará la solicitud de búsqueda al almacén a los robots
12. Los robots recibirán las peticiones de búsqueda de artículos, donde deberán buscar todos los artículos en un tiempo entre [t_min, t_max] con una probabilidad “p” de encontrarlo. Si no encuentran un artículo, todo el pedido quedará como no encontrado
13. El controlador recibirá las respuestas de los robots (mediante una cola específica), en donde, dependiendo de el éxito o fracaso, se actualizará la información y se enviará la orden de entrega a los repartidores
14. Los repartidores recibirán las peticiones de entrega de órdenes, donde deberán buscar todos los artículos en un tiempo entre [t_min, t_max] con una probabilidad “p” de entrega. Dependiendo de su resultado, se dará aviso al controlador
15. Los clientes pueden cancelar los pedidos en cualquier momento, aunque esto no implica que estos pedidos serán efectivamente cancelados
16. Al realizarse una cancelación, el controlador recibirá el pedido y determinará si se puede cancelar (en caso de no haber sido determinado en un estado final), se avisará tanto a robots como a repartidores para que hagan efectiva dicha cancelación
17. En cuanto dicho pedido sea recibido por robots o repartidores, este enviará una confirmación al controlador, quien deberá avisar a todos que dicho pedido ya no necesita ser cancelado.


## 2.3 Requisitos no funcionales
1. Se requiere del intérprete Python 3.6 o superior 
2. Los actuadores pueden ejecutarse ya sea en sistemas Linux o en sistemas Windows
3. Se requieren tener instaladas las librerías especificadas en requires.txt, además de las librerías estándar de Python,
4. Se requiere de una conexión a Internet y la red de UAM para correr el programa de forma correcta
5. Se requiere de un espacio mínimo de disco de 100MB para guardar el código fuente y la base de datos Sqlite
6. El sistema empleado para mantener los datos persistentes será SQLite 
7. Tanto los tiempos de espera como las probabilidades deberán estar definidos en un archivo de configuración de Python
8. Los mensajes recibidos en la cola serán procesados siempre que haya un actor correspondiente (consumidor) que pueda recibirlo
9. En caso de no haber un consumidor, el mensaje permanecerá hasta que exista uno disponible
10. Todos los consumidores de mensajes atenderán un mensaje a la vez, asegurando el fair dispatch. 
11. Los mensajes enviados a las colas se conservarán mientras el servidor de colas permanezca activo
