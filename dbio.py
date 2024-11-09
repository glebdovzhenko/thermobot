import os
import sqlite3
import pandas as pd
import datetime


class DBIO:
    tables = ("users", "cpu", "dht22")

    def __init__(self):
        self._db = os.environ["SQLITEDB"]

    def setup_db(self):
        if os.path.exists(self._db):
            os.remove(self._db)

        connection = sqlite3.connect(self._db)
        cursor = connection.cursor()
        cursor.execute(
            """CREATE TABLE users (
                   id INTEGER PRIMARY KEY, 
                   username TEXT NOT NULL
            );"""
        )
        connection.commit()
        cursor.execute("INSERT INTO users (username) VALUES('glebdovzhenko');")
        connection.commit()
        cursor.execute("INSERT INTO users (username) VALUES('DariaMorgenDorfer');")
        connection.commit()
        cursor.execute(
            """CREATE TABLE cpu (
                   id INTEGER PRIMARY KEY, 
                   date_time INTEGER NOT NULL,
                   temperature REAL NOT NULL 
            );"""
        )
        connection.commit()
        cursor.execute(
            """CREATE TABLE dht22 (
                   id INTEGER PRIMARY KEY, 
                   date_time INTEGER NOT NULL,
                   temperature REAL NOT NULL,
                   humidity REAL NOT NULL
            );"""
        )
        connection.commit()
        connection.close()

    def fetch_allowed_users(self):
        connection = sqlite3.connect(self._db)
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM users")
        allowed_users = cursor.fetchall()
        connection.close()
        return [u[0] for u in allowed_users]

    def append_cpu_reading(self, datetime, temp):
        connection = sqlite3.connect(self._db)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO cpu (date_time, temperature) VALUES (STRFTIME(?), ?)",
            (str(datetime), temp),
        )
        connection.commit()
        connection.close()

    def append_dht_reading(self, datetime, temp, hum):
        connection = sqlite3.connect(self._db)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO dht22 (date_time, temperature, humidity) VALUES (STRFTIME(?), ?, ?)",
            (str(datetime), temp, hum),
        )
        connection.commit()
        connection.close()

    def fetch_cpu_data(self, t_start=None, t_end=None):
        connection = sqlite3.connect(self._db)
        cursor = connection.cursor()
        if t_start is None and t_end is None:
            cmd = "SELECT * FROM cpu"
        elif t_end is None:
            t_end = datetime.datetime.now()
            cmd = (
                "SELECT * FROM cpu WHERE date_time BETWEEN STRFTIME('%s') AND STRFTIME('%s');"
                % (str(t_start), str(t_end))
            )
        elif t_start is None:
            return
        else:
            cmd = (
                "SELECT * FROM cpu WHERE date_time BETWEEN STRFTIME('%s') AND STRFTIME('%s');"
                % (str(t_start), str(t_end))
            )

        cursor.execute(cmd)
        data = cursor.fetchall()
        connection.close()
        data = pd.DataFrame(data)
        data.set_index(0, inplace=True)
        return data
