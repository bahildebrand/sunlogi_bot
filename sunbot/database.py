import psycopg2
from psycopg2.pool import ThreadedConnectionPool


class SunDB:
    def __init__(self):
        self.connPool = ThreadedConnectionPool(5, 20, dbname="postgres",  user="postgres",
                                               host="127.0.0.1", password="password")
        conn = self.connPool.getconn()
        cur = conn.cursor()
        # Create stockpile table
        cur.execute(
            "CREATE TABLE IF NOT EXISTS stockpiles( stockpile_name TEXT PRIMARY KEY, depot TEXT, code INTEGER )")
        # Create message id table
        cur.execute(
            "CREATE TABLE IF NOT EXISTS stockpile_msgs( channel_id TEXT PRIMARY KEY, message_id TEXT )")
        conn.commit()
        cur.close()
        self.connPool.putconn(conn)

    def addStockPile(self, name: str, depot: str, code: int):
        query_string = "INSERT INTO stockpiles(stockpile_name, depot, code) VALUES(%s, %s, %s)"

        conn = self.connPool.getconn()
        cur = conn.cursor()

        values = (name, depot, code)
        cur.execute(query_string, values)
        conn.commit()

        cur.close()
        self.connPool.putconn(conn)

    def getStockPile(self, name: str):
        query_string = f"SELECT (stockpile_name, depot, code) FROM stockpiles WHERE stockpile_name = '{name}'"

        conn = self.connPool.getconn()
        cur = conn.cursor()
        cur.execute(query_string)

        val = cur.fetchone()
        conn.commit()

        cur.close()
        self.connPool.putconn(conn)

    def deleteStockpile(self, name: str):
        query_string = f"DELETE FROM stockpiles WHERE stockpile_name = %s;"

        conn = self.connPool.getconn()
        cur = conn.cursor()
        values = (name,)
        cur.execute(query_string, values)
        rows_deleted = cur.rowcount
        print(f"rows deleted: {rows_deleted}")
        conn.commit()

        cur.close()
        self.connPool.putconn(conn)

    def clearStockpiles(self):
        query_string = "DELETE FROM stockpiles"

        conn = self.connPool.getconn()
        cur = conn.cursor()

        cur.execute(query_string)
        cur.execute(query_string)
        conn.commit()

        cur.close()
        self.connPool.putconn(conn)

    def getAllStockpiles(self):
        query_string = "SELECT * FROM stockpiles"

        conn = self.connPool.getconn()
        cur = conn.cursor()
        cur.execute(query_string)

        stockpiles = cur.fetchall()

        cur.close()
        self.connPool.putconn(conn)

        return stockpiles

    def getMessageId(self, channel_id):
        query_string = f"SELECT message_id FROM stockpile_msgs WHERE channel_id = '{channel_id}'"

        conn = self.connPool.getconn()
        cur = conn.cursor()
        cur.execute(query_string)
        val = cur.fetchone()
        conn.commit()

        cur.close
        self.connPool.putconn(conn)

        return val

    def setMessageId(self, channel_id, message_id):
        query_string = "INSERT INTO stockpile_msgs(channel_id, message_id) VALUES(%s, %s)"

        conn = self.connPool.getconn()
        cur = conn.cursor()

        values = (channel_id, message_id)
        cur.execute(query_string, values)
        conn.commit()

        cur.close()
        self.connPool.putconn(conn)
