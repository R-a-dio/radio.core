from __future__ import unicode_literals
from __future__ import absolute_import
import Queue
import functools

import pymysql
import pymysql.cursors

from . import config


class Cursor(object):
    """
    Establishes a connection to the database and returns an open cursor.


    ```python
    # Use as context manager
    with Cursor() as cur:
        cur.execute(query)
    ```
    """
    _cache = Queue.Queue(maxsize=5)

    def __init__(self, cursor_type=pymysql.cursors.Cursor):
        super(Cursor, self).__init__()

        try:
            conn = self._cache.get_nowait()
        except Queue.Empty:
            conn = pymysql.connect(
                host=config.get("database.host", None),
                user=config.get("database.user", None),
                passwd=config.get("database.pass", None),
                db=config.get("database.name", None),
                port=config.get("database.port", None),
                charset="utf8",
                use_unicode=True,
            )

        self.conn = conn
        self.cursor_type = cursor_type

    def __enter__(self):
        self.cursor = self.conn.cursor(self.cursor_type)
        return self.cursor

    def __exit__(self, type, value, traceback):
        self.cursor.close()
        self.conn.commit()

        # Put it back on the queue
        try:
            self._cache.put_nowait(self.conn)
        except Queue.Full:
            self.conn.close()


DictCursor = functools.partial(Cursor, cursor_type=pymysql.cursors.DictCursor)
