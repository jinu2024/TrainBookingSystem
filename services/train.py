from database import connection, queries

def add_train(train_number, train_name):
    conn = connection.get_connection()
    try:
        if queries.get_train_by_number(conn, train_number):
            raise ValueError("Train number already exists")

        train_id = queries.create_train(conn, train_number, train_name)
        return train_id
    finally:
        connection.close_connection(conn)
