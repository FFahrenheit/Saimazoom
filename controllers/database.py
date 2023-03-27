import sqlite3
import config

class Database:
    def __init__(self):
        try:
            self.connection = sqlite3.connect("db/" + config.database_name)
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()

            if len(tables) == 0:
                self.create_database("db/model.sql")

        except Exception as e:
            self.create_database("db/model.sql")
            print("No se pudo conectar a la base de datos")
            print(e)

    def create_database(self, filename : str):
        try:
            with open(filename, "r") as source:
                sentences = source.readlines()
                for sentence in sentences:
                    print(f"SQL > {sentence}")
                    self.cursor.execute(sentence)
            
            self.connection.commit()
        except Exception as e:
            print(f"No se pudo crear la base de datos")
            print(e)

    def insert_record(self, sentence : str, named_values : tuple):
        try:
            print("SQL > " + sentence)
            self.cursor.execute(sentence, named_values)
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
