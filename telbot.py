from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import sys
import os
import  importlib
import inspect
import glob
from lib.common import Conf
from lib.common import mylogging
from lib.botlib import handler

class cmdbot():
    def __init__(self):
        self.conf =  Conf('conf/botcmd.conf', type='raw')
        self.log = mylogging(self.conf).getLogger()
        rkwargs = None
        proxyurl = self.conf.getConf('telegram', 'proxy_url', None)
        if proxyurl is not None:
            rkwargs = {
                'proxy_url': proxyurl
            }
        
        self.updater = Updater(self.conf.getConf('telegram', 'bottoken'), use_context=True, request_kwargs=rkwargs)
        
        self.handler=[]
        self.loadhandler()
    @staticmethod
    def sortedkey(elem):
        return elem.weight
   

    def loadhandler(self, isreload=False):
        for _script in glob.glob('handlers/*.py'):
            script_name_origin = os.path.basename(_script)
            script_name = script_name_origin.replace('.py', '')
            if script_name.startswith('_'):
                continue
            try:
                module = importlib.import_module('handlers.%s' % script_name)
                if isreload:
                    importlib.reload(module)
                clsz = module.loadhandlers()
                for class_ in clsz:
                    self.handler.append(class_(conf=self.conf))
            except Exception as e:
                self.log.debug('[ERROR] Fail to load script %s' %(script_name))
        self.handler.sort(key=self.sortedkey, reverse=True)
    
    def register_handler(self):
        dispatcher = self.updater.dispatcher
        for hdl in self.handler:
            hdl.register(dispatcher, self)
    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def reload(self):
        self.conf.reload()
        for hdl in self.handler:
            hdl.unregister(self.updater.dispatcher)
        self.handler=[]
        self.loadhandler(isreload=True)
        self.register_handler()

    def stop(self):
        self.updater.stop()
if __name__ == '__main__':
    bot = cmdbot()
    bot.register_handler()
    bot.run()
