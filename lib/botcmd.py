import os
import re
import threading
import subprocess
import json
import sys
sys.path.append(os.getcwd() + '/lib')
sys.path.append(os.getcwd())

from common import Conf
from common import paramChecker
        

class cmdProcessor():
    def __init__(self, conf=None):
        if conf is None:
            self.conf = Conf('conf/botcmd.conf')
        else:
            self.conf = conf
        self.cmd_dic = {}
        self.init_cmdlist()
        self.internal = {
            'help': (self.help, 'show help')
        }
        #self.logger = logger
    def help(self):
        msg = ''
        for k,v in self.cmd_dic.items():
            jsonobj = json.loads(v)
            cmdstr = jsonobj['cmd']
            msg = msg + k + ": " + cmdstr + '\n'
        for k, v in self.internal.items():
            msg = msg + k + ": "  + v[1] + '\n'
        return 0, msg
        #return 0, '\n'.join(self.cmd_dic.keys()) + '\n' + '\n'.join(self.internal.keys())
    def init_cmdlist(self):
        optss = self.conf.getOptions('cmdlist')
        for key, option in optss:
            self.cmd_dic[key] = option
            
    def run(self, key, params, log=None):
        cmdstr = self.cmd_dic.get(key)
        if cmdstr is None:
            cmdtup = self.internal.get(key)
            if cmdtup is None:
                return 2, 'command not found'
            else:
                return cmdtup[0]()
        jsonobj = json.loads(cmdstr)
        opt = jsonobj.get('option')
        objparam = jsonobj.get('params')
        if objparam is None:
            cmdstr = jsonobj['cmd']
        else:
            if len(objparam) > len(params):
                return 3, 'not enough parameters'
            for i in range(0, len(objparam)):
                ptype = objparam[i]
                if not paramChecker.check(params[i], ptype, opt):
                    return 4, 'fail param type check'
            cmdstr = jsonobj['cmd'] %tuple(params[:len(objparam)])
        if log is not None:
            log.debug("exec run cmdstr:%s"%(cmdstr))
        ret = self.runcmd(cmdstr)
        return ret[0], ret[1]

    @staticmethod
    def runcmd(cmdstr):
    # Popen call wrapper.return (code, stdout, stderr)
        child = subprocess.Popen(cmdstr, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = child.communicate()
        ret = child.wait()
        return (ret, out, err)

if __name__ == '__main__':
    conf = Conf('conf/botcmd.conf', type='raw')
    optss = conf.getOptions('cmdlist')
    for option, key in optss:
        print("%s: %s"%(option, key))
    pass