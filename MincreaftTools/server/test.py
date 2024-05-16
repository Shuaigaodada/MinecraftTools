key = "/workspaces/MincreaftTools/private/test.pem"
ip = "3.17.73.191"
user = "Administrator"
port = 22
password = "OYhTqLdO3gQmKB5K4MN3m$@-rbmKL(Ms"

from forge import Forge
from java import Java
from server import Server
import os
MC = "1.20.1"

print("连接中..")
Server( 
       ip, 
       22, 
       key="/workspaces/MincreaftTools/private/test.pem" )\
           .connect("Administrator", password)
print("\r连接成功!")




latest, recommeded = Forge.version(MC)
forge_pack = Forge.download(recommeded)
java_pack = Java.download()



Java.send( java_pack )
Forge.install( forge_pack )

Server().run()

