from database import connection, queries


def add_train(train_number: str, train_name: str) -> int:
    """Create a train and return its id.

    Raises ValueError if the train number already exists.
    """
    conn = connection.get_connection()
    try:
        if queries.get_train_by_number(conn, train_number):
            raise ValueError("Train number already exists")

        return queries.create_train(conn, train_number, train_name)
    finally:
        connection.close_connection(conn)


def update_train(train_id: int, new_name: str) -> None:
    """Update train name by id."""
    conn = connection.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE trains SET train_name = ? WHERE id = ?", (new_name, train_id))
        conn.commit()
    finally:
        connection.close_connection(conn)


def remove_train(train_id: int) -> None:
    """Mark a train as inactive (soft delete)."""
    conn = connection.get_connection()
    try:
        queries.delete_train(conn, train_id)
    finally:
        connection.close_connection(conn)


def list_trains() -> list:
    """Return all trains as a list of rows."""
    conn = connection.get_connection()
    try:
        return queries.get_all_trains(conn)
    finally:
        connection.close_connection(conn)
