import sqlite3
import config

class Database:
    def __init__(self, database=f"{config.db_directory}/{config.database_name}", model=f"{config.db_directory}/{config.db_model}"):
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

    # Funcion para convertir rows de tuplas a diccionarios
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create_database(self, filename: str):
        try:
            with open(filename, "r") as source:
                content = source.read()
                sentences = content.split(";")
                for sentence in sentences:
                    if sentence != "":
                        print(f"SQL > {sentence}")
                        self.cursor.execute(sentence)
    
            self.connection.commit()
        except Exception as e:
            print(f"No se pudo crear la base de datos")
            print(e)

    def insert_record(self, sentence: str, named_values: tuple):
        try:
            print("SQL > " + sentence)
            self.cursor.execute(sentence, named_values)
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(e)
            return False
        
    def update_record(self, sentence: str, named_values: tuple):
        try:
            print("SQL > " + sentence)
            self.cursor.execute(sentence, named_values)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            print(e)
            return False
        
    def get_first(self, sentence: str, named_values: tuple) -> dict:
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
        try:
            print("SQL > " + sentence)
            self.cursor.execute(sentence, named_values)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(e)
            return []
