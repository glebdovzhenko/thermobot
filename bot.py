import os
import datetime

from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from matplotlib import pyplot as plt
import pandas as pd
from dbio import DBIO


class Bot:
    def __init__(self):
        self._token = os.environ["TG_BOT_TOKEN"]
        self._dbio = DBIO()
        self._allowed_users = self._dbio.fetch_allowed_users()

    def _check_user(self, update: Update):
        return update.effective_user.username in self._allowed_users

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._check_user(update):
            return

        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )

    async def plot_last_hour(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not self._check_user(update):
            return

        t_data = self._dbio.fetch_dht_data(
            t_end=datetime.datetime.now(),
            t_start=datetime.datetime.now() - datetime.timedelta(hours=1),
        )

        fig, ax1 = plt.subplots()

        color = "tab:red"
        ax1.set_xlabel("time (s)")
        ax1.set_ylabel("Temperature [C]", color=color)
        ax1.plot(pd.to_datetime(t_data[1]), t_data[2], color=color)
        ax1.tick_params(axis="y", labelcolor=color)

        ax2 = ax1.twinx()  # instantiate a second Axes that shares the same x-axis

        color = "tab:blue"
        ax2.set_ylabel(
            "Humidity", color=color
        )  # we already handled the x-label with ax1
        ax2.plot(pd.to_datetime(t_data[1]), t_data[3], color=color)
        ax2.tick_params(axis="y", labelcolor=color)

        fig.tight_layout()
        plt.savefig("response.png")
        plt.close(fig)

        await update.message.reply_photo("response.png")

    async def plot_last_day(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not self._check_user(update):
            return

        t_data = self._dbio.fetch_dht_data(
            t_end=datetime.datetime.now(),
            t_start=datetime.datetime.now() - datetime.timedelta(days=1),
        )

        fig, ax1 = plt.subplots()

        color = "tab:red"
        ax1.set_xlabel("time (s)")
        ax1.set_ylabel("Temperature [C]", color=color)
        ax1.plot(pd.to_datetime(t_data[1]), t_data[2], color=color)
        ax1.tick_params(axis="y", labelcolor=color)

        ax2 = ax1.twinx()  # instantiate a second Axes that shares the same x-axis

        color = "tab:blue"
        ax2.set_ylabel(
            "Humidity", color=color
        )  # we already handled the x-label with ax1
        ax2.plot(pd.to_datetime(t_data[1]), t_data[3], color=color)
        ax2.tick_params(axis="y", labelcolor=color)

        fig.tight_layout()
        plt.savefig("response.png")
        plt.close(fig)

        await update.message.reply_photo("response.png")

    def run(self):
        application = Application.builder().token(self._token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("last_hour", self.plot_last_hour))
        application.add_handler(CommandHandler("last_day", self.plot_last_day))

        # application.add_handler(
        #     MessageHandler(filters.TEXT & ~filters.COMMAND, self.respond)
        # )

        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # main()
    bot = Bot()
    bot.run()
