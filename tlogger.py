import asyncio
import os
import sys
import sqlite3
import datetime

from dbio import DBIO


class Thermometer:
    @staticmethod
    def get_cpu():
        """
        Returns current CPU temperature as int in degrees C.
        """
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read()) // 1000

    def __init__(self):
        self._dbio = DBIO()

    def measure_once(self):
        self._dbio.append_temp_reading(datetime.datetime.now(), self.get_cpu())

    async def measure_infinite(self, period: int = 1):
        while True:
            self.measure_once()
            await asyncio.sleep(period)


if __name__ == "__main__":
    th = Thermometer()

    loop = asyncio.get_event_loop()
    # loop.call_later(5, stop)
    task = loop.create_task(th.measure_infinite())

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        pass
