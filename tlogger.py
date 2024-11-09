import asyncio
import datetime
import os
import numpy as np

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

    async def measure_infinite(self):
        while True:
            dt = int(os.environ["MEAS_PERIOD"])
            n_steps = int(os.environ["MEAS_PTS"])

            cpu_t, dht_t, dht_h = (
                np.empty(n_steps),
                np.empty(n_steps),
                np.empty(n_steps),
            )
            cpu_t[:] = np.NaN
            dht_t[:] = np.NaN
            dht_h[:] = np.NaN

            for ii in range(n_steps):
                try:
                    cpu_t[ii] = self.get_cpu()
                except Exception as err:
                    print(err)

                if self._dht is not None:
                    try:
                        dht_t[ii] = self._dht.temperature
                    except RuntimeError as re:
                        print(re.args[0])
                    except Exception as err:
                        self._dht.exit()
                        raise err
                    try:
                        dht_h[ii] = self._dht.humidity
                    except RuntimeError as re:
                        print(re.args[0])
                    except Exception as err:
                        self._dht.exit()
                        raise err

                await asyncio.sleep(dt / (n_steps - 1))

            print(datetime.datetime.now())
            if not np.all(np.isnan(cpu_t)):
                print(
                    "CPU: [%.01f, %.01f], %d / %d fails, %.01f ± %.01f"
                    % (
                        np.nanmin(cpu_t),
                        np.nanmax(cpu_t),
                        np.isnan(cpu_t).sum(),
                        n_steps,
                        np.nanmean(cpu_t),
                        np.nanstd(cpu_t),
                    )
                )
                self._dbio.append_cpu_reading(
                    datetime.datetime.now(), np.nanmean(cpu_t), verbose=False
                )

            if (not np.all(np.isnan(dht_t))) and (not np.all(np.isnan(dht_h))):
                print(
                    "DHT22 T: [%.01f, %.01f], %d / %d fails, %.01f ± %.01f"
                    % (
                        np.nanmin(dht_t),
                        np.nanmax(dht_t),
                        np.isnan(dht_t).sum(),
                        n_steps,
                        np.nanmean(dht_t),
                        np.nanstd(dht_t),
                    )
                )
                print(
                    "DHT22 H: [%.01f, %.01f], %d / %d fails, %.01f ± %.01f"
                    % (
                        np.nanmin(dht_h),
                        np.nanmax(dht_h),
                        np.isnan(dht_h).sum(),
                        n_steps,
                        np.nanmean(dht_h),
                        np.nanstd(dht_h),
                    )
                )
                self._dbio.append_dht_reading(
                    datetime.datetime.now(),
                    np.nanmean(dht_t),
                    np.nanmean(dht_h),
                    verbose=False,
                )


if __name__ == "__main__":
    th = Thermometer()

    loop = asyncio.get_event_loop()
    # loop.call_later(5, stop)
    task = loop.create_task(th.measure_infinite())

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        pass
