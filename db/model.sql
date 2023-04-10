CREATE TABLE user(
    username TEXT PRIMARY KEY, 
    password TEXT, 
    name TEXT
);;

CREATE TABLE orders(
    id INTEGER PRIMARY KEY, 
    status TEXT DEFAULT "Creado" NOT NULL,
    description TEXT,
    total INTEGER,
    client TEXT NOT NULL,
    FOREIGN KEY (client)
        REFERENCES user(username)
);;

CREATE TABLE log(
    id INTEGER PRIMARY KEY,
    status TEXT NOT NULL,
    time DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_id INT NOT NULL,
    FOREIGN KEY (order_id)
        REFERENCES orders(id)
);;

CREATE TRIGGER order_log
AFTER INSERT
ON orders
BEGIN
  INSERT INTO log (status, order_id)
  VALUES (
    NEW.status,
    NEW.id
  );
END;;

CREATE TRIGGER order_log_update
AFTER UPDATE
ON orders
BEGIN
  INSERT INTO log (status, order_id)
  VALUES (
    NEW.status,
    NEW.id
  );
END;;