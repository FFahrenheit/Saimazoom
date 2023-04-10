import sqlite3
import config

class Database:
    def __init__(self, database=f"{config.db_directory}/{config.database_name}", model=f"{config.db_directory}/{config.db_model}"):
        """
        Constructor de la clase Database que se encarga de conectarse a la base de datos indicada.
        Si la conexión no es exitosa, entonces se crea la base de datos a partir del archivo SQL.
        
        Args:
        - database (str): ruta del archivo de la base de datos.
        - model (str): ruta del archivo SQL que se utilizará para crear la base de datos.
        """
        try:
            self.database = database
            self.model = model
            self.connection = sqlite3.connect(self.database)
            self.connection.row_factory = self.dict_factory
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()

            if len(tables) == 0:
                self.create_database(self.model)

        except Exception as e:
            self.create_database(self.model)
            print("No se pudo conectar a la base de datos")
            print(e)

    def dict_factory(self, cursor, row):
        """
        Función que convierte una fila de tupla en un diccionario con claves iguales a los nombres de las columnas.

        Args:
        - cursor: objeto que representa el cursor utilizado en la conexión de la base de datos.
        - row: fila de tupla.

        Returns:
        - d (dict): diccionario con claves iguales a los nombres de las columnas y valores igual a la fila de tupla.
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create_database(self, filename: str):
        """
        Función que se encarga de crear la base de datos a partir del archivo SQL especificado.

        Args:
        - filename (str): ruta del archivo SQL que se utilizará para crear la base de datos.
        """
        try:
            with open(filename, "r") as source:
                content = source.read()
                sentences = content.split(";;")
                for sentence in sentences:
                    if sentence != "":
                        print(f"SQL > {sentence}")
                        self.cursor.execute(sentence)
    
            self.connection.commit()
        except Exception as e:
            print(f"No se pudo crear la base de datos")
            print(e)

    def insert_record(self, sentence: str, named_values: tuple):
        """
        Función que inserta un registro en la base de datos.

        Args:
        - sentence (str): sentencia SQL que se utilizará para insertar el registro.
        - named_values (tuple): valores que se insertarán en la tabla.

        Returns:
        - lastrowid (int): el ID del último registro insertado.
        - False: si no se pudo insertar el registro.
        """
        try:
            print("SQL > " + sentence)
            self.cursor.execute(sentence, named_values)
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(e)
            return False
        
    def update_record(self, sentence: str, named_values: tuple):
        """
        Función que actualiza un registro en la base de datos.

        Args:
        - sentence (str): sentencia SQL que se utilizará para actualizar el registro.
        - named_values (tuple): valores que se actualizarán en la tabla.

        Returns:
        - rowcount (int):
        """
        try:
            print("SQL > " + sentence)
            self.cursor.execute(sentence, named_values)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            print(e)
            return False


    def get_first(self, sentence: str, named_values: tuple) -> dict:
        """
        Obtiene el primer registro que coincida con la consulta.

        Args:
            sentence (str): La consulta SQL.
            named_values (tuple): Los valores que se van a pasar a la consulta.

        Returns:
            dict: El primer registro que coincide con la consulta.
                  Si no se encuentra ningún registro, devuelve `None`.
        """
        try:
            print("SQL > " + sentence)
            self.cursor.execute(sentence, named_values)
            rows = self.cursor.fetchall()
            if len(rows) > 0:
                return rows[0]
            return None
        except Exception as e:
            print(e)
            return None
    

    def get_select(self, sentence: str, named_values: tuple) -> list:
        """
        Obtiene una lista de registros que coincidan con la consulta.

        Args:
            sentence (str): La consulta SQL.
            named_values (tuple): Los valores que se van a pasar a la consulta.

        Returns:
            list: Una lista de registros que coinciden con la consulta.
                  Si no se encuentra ningún registro, devuelve una lista vacía.
        """
        try:
            print("SQL > " + sentence)
            self.cursor.execute(sentence, named_values)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(e)
            return []