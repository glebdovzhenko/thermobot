import os
import sqlite3
import pandas as pd
import datetime


class DBIO:
    def __init__(self):
        self._db = os.environ["SQLITEDB"]

    def fetch_allowed_users(self):
        connection = sqlite3.connect(self._db)
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM users")
        allowed_users = cursor.fetchall()
        connection.close()
        return [u[0] for u in allowed_users]

    def append_temp_reading(self, datetime, temp):
        connection = sqlite3.connect(self._db)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO temperature (date_time, temp) VALUES (STRFTIME(?), ?)",
            (str(datetime), temp),
        )
        connection.commit()
        connection.close()

    def fetch_temp_data(self, t_start=None, t_end=None):
        connection = sqlite3.connect(self._db)
        cursor = connection.cursor()
        if t_start is None and t_end is None:
            cmd = "SELECT * FROM temperature"
        elif t_end is None:
            t_end = datetime.datetime.now()
            cmd = (
                "SELECT * FROM temperature WHERE date_time BETWEEN STRFTIME('%s') AND STRFTIME('%s');"
                % (str(t_start), str(t_end))
            )
        elif t_start is None:
            return
        else:
            cmd = (
                "SELECT * FROM temperature WHERE date_time BETWEEN STRFTIME('%s') AND STRFTIME('%s');"
                % (str(t_start), str(t_end))
            )

        cursor.execute(cmd)
        data = cursor.fetchall()
        connection.close()
        data = pd.DataFrame(data)
        data.set_index(0, inplace=True)
        return data


def get_bot_token():
    return os.environ["TG_BOT_TOKEN"]
