from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from lib.common import mylogging
from lib.botlib import handler
from lib.botcmd import cmdProcessor
from telegram.ext import BaseFilter
def loadhandlers():
    return [defaulthandler, starthandler,cmdhandler]

class defaulthandler(handler):
    def __init__(self, conf=None):
        super(defaulthandler, self).__init__(conf)
    

class starthandler(handler):
    def __init__(self, conf=None):
        super(starthandler, self).__init__(conf)
        self.version='1.0'
        self.weight = 6
        self.name = 'start'
        self.myhandler = CommandHandler(self.name, self.worker, filters=self.getFilters())

    def proceed(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Greetings,you can talk to me now')


class testhandler(handler):
    def __init__(self, conf=None):
        super(testhandler, self).__init__(conf)
        self.version='1.0'
        self.weight = 3
        self.name = 'test'
        self.myhandler = MessageHandler(Filters.all, self.worker)

    def proceed(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='This is a test')

class mediahandler(handler):
    def __init__(self, conf=None):
        super(mediahandler, self).__init__(conf)
        self.version='1.0'
        self.weight = 3
        self.name = 'media'
        self.myhandler = MessageHandler(self.getFilters((Filters.photo | Filters.video)), self.worker)
    def proceed(self, update, context):
        photoes = update.effective_message.photo
        filesize = 0
        fileid = ''
        if photoes is not None and len(photoes) > 0:
            photo = photoes[len(photoes) -1]
            pfile = photo.get_file()
            filesize = pfile.file_size
            fileid = pfile.file_unique_id
            pfile.download()
        video = update.effective_message.video
        if video is not None:
            vfile = video.get_file()
            vfile.download(custom_path='data')
            fileid = vfile.file_unique_id
            filesize = vfile.file_size
        context.bot.send_message(chat_id=update.effective_chat.id, text='downloading %s, filezie=%d'%(fileid, filesize))
        #838208442, private, supergroup, effective_chat, effective_message.effective_attachement

class cmdhandler(handler):
    def __init__(self, conf=None):
        super(cmdhandler, self).__init__(conf)
        self.version='1.0'
        self.weight = 2
        self.name = 'exec'
        self.needauth = True
        self.myhandler = CommandHandler(self.name,self.worker, filters=self.getFilters())
        self.cmdp = cmdProcessor(self.conf)
    
    def proceed(self, update, context):
        if len(context.args) > 0:
            params = None
            cmd = context.args[0]
            if len(context.args) < 2:
                params = []
            else:
                params = context.args[1:]
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='no executed command provide')
        ret, msg = self.cmdp.run(cmd, params, self.log)
        try:
            if type(msg) == bytes:
                msg = msg.decode()
        except UnicodeDecodeError as e:
            self.log.debug('msg decode exception, type=%s'%(str(type(e))))
            msg = msg.decode('gb2312')
        sended = 0
        while sended < len(msg):
            if len(msg) - sended >= 4096:
                context.bot.send_message(chat_id=update.effective_chat.id, text=msg[sended:sended+4096])
                sended = sended + 4096
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=msg[sended:len(msg)])
                sended = len(msg)