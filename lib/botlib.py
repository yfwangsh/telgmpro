from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import sys
import os
sys.path.append(os.getcwd() + '/lib')
sys.path.append(os.getcwd())
from common import mylogging
class handler():
    def __init__(self, conf=None, bot=None):
        self.version='1.0'
        self.weight = -1
        self.name = 'default'
        self.registered = True
        self.log = mylogging(conf).getLogger()
        self.myhandler = MessageHandler(self.getFilters(Filters.command), self.worker)
        self.conf = conf
        self.needauth = False
        self.bot = None
    
    ## this bot default to work on private chat
    def getFilters(self, newfilter=None): 
        if newfilter is None:
            return Filters.private
        return Filters.private & newfilter 
        
    def worker(self, update, context):
        if self.doauthorized(update):
            self.proceed(update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, need authorized before process that command")

    def proceed(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

    def register(self, dispatcher, bot):
        if self.registered:
            dispatcher.add_handler(self.myhandler)
        else:
            self.log.debug("%s handler is not enabled"%(self.name,))
        self.bot = bot
    def unregister(self, dispatcher):
        if self.registered:
            dispatcher.remove_handler(self.myhandler)
    
    def doauthorized(self, update):
        if self.needauth:
            str_aids = self.conf.getConf('telegram', 'authorized_ids')
            aids = str_aids.split(';') 
            for aid in aids:
                try:
                    effid = int(aid)
                    if update.effective_user.id == effid:
                        return True
                except Exception:
                    pass
        else:
            return True
        return False

