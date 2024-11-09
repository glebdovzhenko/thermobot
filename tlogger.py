import asyncio
import datetime
import os

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
        self._dht = None
        try:
            self._board = __import__("board")
            self._adafruit_dht = __import__("adafruit_dht")
            self._dht = self._adafruit_dht.DHT22(self._board.D4, use_pulseio=False)
        except Exception as e:
            print(e)

    def measure_once(self):
        self._dbio.append_cpu_reading(datetime.datetime.now(), self.get_cpu())
        if self._dht is not None:
            try:
                self._dbio.append_dht_reading(
                    datetime.datetime.now(), self._dht.temperature, self._dht.humidity
                )
            except RuntimeError as re:
                print(re.args[0])
            except Exception as err:
                self._dht.exit()
                raise err

    async def measure_infinite(self, period: int = 1):
        while True:
            dt = int(os.environ["MEAS_PERIOD"])
            n_steps = os.environ["MEAS_PTS"]
            self.measure_once()
            await asyncio.sleep(dt)


if __name__ == "__main__":
    th = Thermometer()

    loop = asyncio.get_event_loop()
    # loop.call_later(5, stop)
    task = loop.create_task(th.measure_infinite())

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        pass
