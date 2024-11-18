def get_items(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, description FROM items")
        items = cursor.fetchall()
        return [{"id": item[0], "name": item[1], "description": item[2]} for item in items]

def get_item(connection, item_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, description FROM items WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        if item:
            return {"id": item[0], "name": item[1], "description": item[2]}
        return None

def create_item(connection, name, description):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id",
            (name, description)
        )
        connection.commit()
        return cursor.fetchone()[0]
