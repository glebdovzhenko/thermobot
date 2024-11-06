import os
import datetime

from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from matplotlib import pyplot as plt
import pandas as pd
from dbio import DBIO, get_bot_token


class Bot:
    def __init__(self):
        self._token = get_bot_token()
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

        t_data = self._dbio.fetch_temp_data(
            t_end=datetime.datetime.now(),
            t_start=datetime.datetime.now() - datetime.timedelta(hours=1),
        )
        fig = plt.figure()
        plt.plot(pd.to_datetime(t_data[1]), t_data[2])
        plt.savefig("response.png")
        plt.close(fig)

        await update.message.reply_photo("response.png")

    async def plot_last_day(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not self._check_user(update):
            return

        t_data = self._dbio.fetch_temp_data(
            t_end=datetime.datetime.now(),
            t_start=datetime.datetime.now() - datetime.timedelta(days=1),
        )
        fig = plt.figure()
        plt.plot(pd.to_datetime(t_data[1]), t_data[2])
        plt.savefig("response.png")
        plt.close(fig)

        await update.message.reply_photo("response.png")

    def run(self):
        application = Application.builder().token(os.environ["TG_BOT_TOKEN"]).build()

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
