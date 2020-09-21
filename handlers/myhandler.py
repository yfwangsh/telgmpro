from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from lib.common import mylogging
from lib.botlib import handler

def loadhandlers():
    return [reloadhandler]

class reloadhandler(handler):
    def __init__(self, conf=None):
        super(reloadhandler, self).__init__(conf)
        self.version='1.0'
        self.weight = 3
        self.name = 'reload'
        self.needauth = True
        self.myhandler = CommandHandler(self.name, self.worker)
    def proceed(self, update, context):
        if self.bot is not None:
            self.bot.reload()
            context.bot.send_message(chat_id=update.effective_chat.id, text='Done reload')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Bot not reload')

