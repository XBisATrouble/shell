# -*- coding: UTF-8 -*-
import os
import sys
import shlex
import getpass
import socket
import signal
import subprocess
import platform
from my_builtins import *

built_in_cmds={}

def register_command(name,func):
    """
    注册命令,使命令与相应处理函数建立映射关系
    :param name: 命令名
    :param func: 函数名
    """
    built_in_cmds[name]=func

def init():
    """
    注册所有命令
    :return:
    """

    register_command("cd",cd)
    register_command("exit",exit)
    register_command("getenv",getenv)
    register_command("history",history)

def shell_loop():
    """
    主体循环
    :return:
    """
    status=SHELL_STATUS_RUN

    while status== SHELL_STATUS_RUN:
        display_cmd_prompt()

        ignore_signals()

        try:
            cmd=sys.stdin.readline()

            cmd_tokens=tokensize(cmd)

            cmd_tokens=preprocess(cmd_tokens)

            status=execute(cmd_tokens)
        except:
            _,err,_ = sys.exc_info()
            print(err)

def main():
    init()
    shell_loop()


#展示命令提示符
def display_cmd_prompt():
    user=getpass.getuser()

    hostname=socket.gethostname()

    cwd=os.getcwd()

    #获得最低级目录
    base_dir=os.path.basename(cwd)

    home_dir=os.path.expanduser('~')
    if cwd==home_dir:
        base_dir='~'

    sys.stdout.write("[\033[1;33m%s\033[0;0m@%s \033[1;36m%s\033[0;0m] $ " % (user, hostname, base_dir))
    sys.stdout.flush()

def ignore_signals():
    signal.signal(signal.SIGTSTP,signal.SIG_IGN)
    signal.signal(signal.SIGINT,signal.SIG_IGN)

def tokensize(string):
    return shlex.split(string)

def preprocess(tokens):
    processed_tokens=[]
    for token in tokens:
        if token.startswith('$'):
            processed_tokens.append(os.getenv(token[1:])) #getenv用于获取环境变量
        else:
            processed_tokens.append(token)

    return processed_tokens

def handler_kill(signum,frame):
    raise OSError("killed!")
def execute(cmd_tokens):
    with open(HISTORY_PATH,'a') as history_file:
        history_file.write(' '.join(cmd_tokens)+os.linesep)

    if cmd_tokens:
        cmd_name = cmd_tokens[0]
        cmd_args = cmd_tokens[1:]

        if cmd_name in built_in_cmds:
            return built_in_cmds[cmd_name](cmd_args)

    signal.signal(signal.SIGINT,handler_kill)

    p=subprocess.Popen(cmd_tokens)

    p.communicate()

    return SHELL_STATUS_RUN

if __name__ == '__main__':
    main()
