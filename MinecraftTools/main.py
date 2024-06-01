from server import Server
from forge import Forge
from java import Java

import os
import sys
<<<<<<< HEAD
import configparser
from loguru import logger
=======
import time
import configparser
>>>>>>> da1dd93 (v1.0)
from paramiko.ssh_exception import SSHException

if getattr(sys, 'frozen', False):
    # frozen
    path = sys._MISPASS
else:
    path = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read( os.path.join( path, "config", "server.cfg" ) )

if not config.sections():
    Server.create_file()
    print("已生成配置文件，请修改配置文件后再次运行文件")
    exit(0)
<<<<<<< HEAD
Server.create_file()

=======
>>>>>>> da1dd93 (v1.0)

hosts = config.get("Server", "hosts")
port = config.getint("Server", "port")
user = config.get("Server", "user")
password = config.get("Server", "password")
key = config.get("Server", "key")
MC_VERSION = config.get("MC", "version")
Forge_VERSION = config.get("Forge", "version")

hosts = hosts if hosts != "" else None
port = port if port != "" else None
user = user if user != "" else None
password = password if password != "" else None
key = key if key != "" else None
MC_VERSION = MC_VERSION if MC_VERSION != "" else None
Forge_VERSION = Forge_VERSION if Forge_VERSION != "" else None

if hosts == None:
    print("服务器地址不能为空")
    exit(0)
if port == None:
    print("端口不能为空")
    exit(0)
if user == None:
    print("用户名不能为空")
    exit(0)
if MC_VERSION == None:
    print("Minecraft版本不能为空")
    exit(0)

print("服务器信息:")
print("Hosts: %s" % hosts)
print("Port: %s" % port)
print("User: %s" % user)
print("Password: %s" % password)
print("Key: %s" % key)
print("Minecraft Version: %s" % MC_VERSION)
print("Forge Version: %s" % Forge_VERSION)

<<<<<<< HEAD
logger.info("正在连接服务器...")
=======
>>>>>>> da1dd93 (v1.0)
server = Server( hosts, port, key )
try:
    server.connect(user, password)
except SSHException:
    print("连接失败, 是否缺少密钥文件或是密码错误")
    exit(1)
<<<<<<< HEAD
except TimeoutError:
    print("连接失败, 服务器连接超时")
    exit(1)
    

logger.info("连接成功")
=======
>>>>>>> da1dd93 (v1.0)

server.MC_VERSION = MC_VERSION
server.MC_PATH = server.basepath + "\\" + f"forge_{MC_VERSION}_server"

<<<<<<< HEAD
def check(cmd: str) -> None:
    if cmd == "taskkill -all":
        _, stdout, _ = server.send("tasklist")
        kills_task_pid = []
        output = stdout.read().decode()
        for task in output.splitlines():
            if "cmd.exe" in task:
                kills_task_pid.append(task.split()[1])
        print(kills_task_pid)
        for pid in kills_task_pid:
            server.send(f"taskkill /F /PID {pid}")
            print(f"已结束进程: {pid}")
=======
>>>>>>> da1dd93 (v1.0)

try:
    while True:
        print("1. 初始化服务器")
        print("2. 启动服务器")
<<<<<<< HEAD
        print("3. 关闭服务器")
        print("4. 退出")
        try:
            choose = input("请输入选择: ")
            check(choose)
=======
        print("3. 退出")
        try:
            choose = input("请输入选择: ")
>>>>>>> da1dd93 (v1.0)
            choose = int(choose)
        except ValueError:
            print("输入错误")
            continue
        
        if choose == 1:
            lastest, recommended = Forge.version( MC_VERSION )
            print("请选择Forge版本")
            print("1. 最新版本: %s" % lastest)
            print("2. 推荐版本: %s" % recommended)
            version = None
            while True:
                try:
                    choose = input("请输入选择: ")
                    choose = int(choose)
                except ValueError:
                    print("输入错误")
                    continue
                if choose == 1:
                    version = lastest
                elif choose == 2:
                    version = recommended
                else:
                    print("输入错误")
                    continue
                break
            pack = Java.download()
            forge_path = Forge.download( version )
            
            Java.send( pack )
<<<<<<< HEAD
            server.reconnect()
            Forge.install(forge_path)
            server.reconnect()
            print("初始化完成")
        elif choose == 2:
            if not server.check():
                server.run()
                logger.info("服务器启动成功")
            else:
                logger.info("服务器已经启动")
            exit()
                
        elif choose == 3:
            server.kill_server()
            logger.info("服务器已关闭")
            break
        
        elif choose == 4:
=======
            Forge.install(forge_path)
            print("初始化完成")
        elif choose == 2:
            stdin, stdout, stderr = server.exec(f"cd /d {server.MC_PATH} && .\\run.bat")
            while True:
                cmd = input(">>> ")
                if cmd == "exit":
                    stdin.close()
                    stdout.close()
                    stderr.close()
                    break
                stdin.write(cmd + "\n")
                stdin.flush()
                print()
                
        elif choose == 3:
>>>>>>> da1dd93 (v1.0)
            break
finally:
    server.close()
        
        
    
