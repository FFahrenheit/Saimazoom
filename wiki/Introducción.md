# 1. Introducción
Este proyecto consiste en la implementación de una aplicación de simulación de entrega de paquetes inspirada en el servicio de Amazon. La aplicación se divide en diferentes componentes que incluyen un cliente, un controlador, robots y el servicio de entrega en sí. La interacción entre estos componentes se realiza mediante colas de mensajes.
El objetivo principal de esta aplicación es proporcionar una simulación del proceso de entrega de paquetes de Amazon(Saimazoom), donde los usuarios pueden enviar solicitudes de entrega y hacer un seguimiento del progreso de sus pedidos. Para lograr este objetivo, se ha desarrollado una arquitectura basada en colas de mensajes, que permite la comunicación y coordinación entre los diferentes componentes de la aplicación, además de facilitar la escalabilidad de la aplicación, aumentar su tolerancia a fallos y simplificar su desarrollo..
En este trabajo, se describe en detalle la arquitectura de la aplicación, incluyendo su diseño y las tecnologías utilizadas. También se presentarán los diferentes componentes de la aplicación y cómo interactúan entre sí para lograr el objetivo final 

## 1.1 Objetivo

El objetivo de Saimazoom es el de crear un sistema para la gestión de pedidos online. Este sistema debe incluir a los actores:
* **Cliente**, que realiza y gestiona pedidos de productos.
* **Controlador** central, que gestiona todo el proceso.
* **Robots**, que se encargan de buscar los productos en el almacén y colocarlos en las cintas transportadoras.
* **Repartidores**, encargados de transportar el producto a la casa del cliente

El sistema debe de gestionar las interacciones entre todos estos actores, para las comunicaciones correspondientes se empleará una cola de mensajes.
