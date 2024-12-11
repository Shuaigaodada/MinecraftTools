import os
import jdk
import forge
import signal
import subprocess
import platform
from loguru import logger

prefab = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prefabs")
basepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "server")
logger.info(f"执行 mkdir -p {basepath}")
# 创建目录
os.makedirs(basepath, exist_ok=True)

class Server:
    def __init__(self, jdk: jdk.JDK, forge: forge.Forge):
        self.jdk = jdk
        self.forge = forge
        if self.jdk.path is None:
            print("请先下载JDK")
            return
        if self.forge.path is None:
            print("请先下载Forge")
            return
        java_executable = "java.exe" if platform.system() == "Windows" else "java"
        self.java_path = os.path.join(self.jdk.path, "bin", java_executable)
        self.server_path = os.path.join(basepath, self.forge.minecraft_version, self.forge.version)
    

    def install(self):
        """安装服务端"""
        if not os.path.exists(os.path.join(basepath, self.forge.minecraft_version)):
            os.makedirs(os.path.join(basepath, self.forge.minecraft_version))
        if not os.path.exists(os.path.join(basepath, self.forge.minecraft_version, self.forge.version)):
            os.makedirs(os.path.join(basepath, self.forge.minecraft_version, self.forge.version))
        
        self.server_path = os.path.join(basepath, self.forge.minecraft_version, self.forge.version)
        
        logger.info(f"执行 {self.java_path} -jar {self.forge.path} --installServer")
        try:
            process = subprocess.Popen([
                self.java_path,
                "-jar",
                self.forge.path,
                "--installServer"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=self.server_path)
        except FileNotFoundError:
            print(self.forge.path)
            print(self.java_path)
            return
        
        for line in iter(process.stdout.readline, ''):
            if line:
                yield line.strip()
        
        process.stdout.close()
        process.wait()

    def replace(self):
        """替换服务端文件"""
        bat_prefab = os.path.join(prefab, "run.bat") if os.path.exists(os.path.join(self.server_path, "run.bat")) else os.path.join(prefab, "1.13-run.bat")
        with open(bat_prefab, "r") as f:
            content = f.read()
        content = content.replace("JAVA_PATH", self.java_path).replace("FORGE_PATH", os.path.join(self.server_path, f"forge-{self.forge.minecraft_version}-{self.forge.version}.jar"))
        with open(os.path.join(self.server_path, "run.bat"), "w") as f:
            f.write(content)
            
        with open(os.path.join(prefab, "eula.txt"), "r") as f:
            content = f.read()
        with open(os.path.join(self.server_path, "eula.txt"), "w") as f:
            f.write(content)
        
        
        
    
    def init(self):
        """初始化服务端
        """
        logger.info("初始化服务端")
        bat_file_path = os.path.join(self.server_path, "run.bat")
        process = subprocess.Popen([
            bat_file_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=self.server_path)
        
        for line in iter(process.stdout.readline, ''):
            if line:
                yield line.strip()
                if "Done" in line:
                    process.terminate()
                    process.wait()  # 等待进程完全退出
                    logger.info("服务端初始化完成 杀死进程")
                    break
        
        process.stdout.close()
        process.wait()
    

if __name__ == "__main__":
    logger.info("开始执行程序")
    _forge = forge.ForgeVersion("1.13.2").latest
    _jdk = jdk.JDK("1.13.2")
    
    for total, chunk in _forge.download():
        print(f"{chunk}/{total}")
    
    for total, chunk in _jdk.download():
        print(f"{chunk}/{total}")
    
    server = Server(_jdk, _forge)
    
    for output in server.install():
        print(output)
    server.replace()
    for output in server.init():
        print(output)
    from properties import Properties
    properties = Properties()
    properties.difficulty = "hard"
    properties.level_name = "myserver"
    properties.save(server.server_path)
    logger.info("程序执行完毕")