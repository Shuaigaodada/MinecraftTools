import os
import jdk
import path
import forge
import platform
import properties
import subprocess
from loguru import logger



logger.info(f"执行 mkdir -p {path.server}")
# 创建目录
os.makedirs(path.server, exist_ok=True)

def kill_process_on_port(port):
    # 查找占用端口的进程 ID
    result = subprocess.run(f'netstat -ano | findstr :{port}', shell=True, capture_output=True, text=True)
    if result.stdout:
        # 提取进程 ID
        lines = result.stdout.strip().split('\n')
        for line in lines:
            parts = line.split()
            pid = parts[-1]
            # 终止进程
            subprocess.run(f'taskkill /PID {pid} /F', shell=True)
            logger.info(f"已终止占用端口 {port} 的进程，PID: {pid}")
    else:
        logger.info(f"没有找到占用端口 {port} 的进程")

class Server:
    def __init__(self, jdk: jdk.JDK, forge: forge.Forge):
        self.jdk = jdk
        self.forge = forge
        self.properties = properties.Properties()
        self.path = None
    
    def install(self):
        """安装服务端"""
        if not os.path.exists(os.path.join(path.server, self.forge.minecraft_version)):
            os.makedirs(os.path.join(path.server, self.forge.minecraft_version))
        if not os.path.exists(os.path.join(path.server, self.forge.minecraft_version, self.forge.version)):
            os.makedirs(os.path.join(path.server, self.forge.minecraft_version, self.forge.version))
        
        java_executable = "java.exe" if platform.system() == "Windows" else "java"
        self.java_path = os.path.join(self.jdk.path, "bin", java_executable)
        
        self.path = os.path.join(path.server, self.forge.minecraft_version, self.forge.version)
        
        logger.info(f"执行 {self.java_path} -jar {self.forge.path} --installServer")
        try:
            process = subprocess.Popen([
                self.java_path,
                "-jar",
                self.forge.path,
                "--installServer"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=self.path)
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
        _, ver, _ = self.forge.minecraft_version.split(".")
        if int(ver) <= 13:
            bat_prefab = os.path.join(path.prefabs, "1.13-run.bat")
        else:
            bat_prefab = os.path.join(path.prefabs, "run.bat")
        
        with open(bat_prefab, "r") as f:
            content = f.read()
        content = content.replace("JAVA_PATH", self.java_path).replace("FORGE_PATH", os.path.join(self.path, f"forge-{self.forge.minecraft_version}-{self.forge.version}.jar"))
        with open(os.path.join(self.path, "run.bat"), "w") as f:
            f.write(content)
            
        with open(os.path.join(path.prefabs, "eula.txt"), "r") as f:
            content = f.read()
        with open(os.path.join(self.path, "eula.txt"), "w") as f:
            f.write(content)
    
    def init(self):
        """初始化服务端"""
        logger.info("初始化服务端")
        self.properties.save(self.path)
        bat_file_path = os.path.join(self.path, "run.bat")
        process = subprocess.Popen([
            bat_file_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=self.path)
        
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield line.strip()
                    if "Done" in line:
                        logger.info("服务端初始化完成，终止进程")
                        process.terminate()
                        process.wait(timeout=10)  # 等待进程完全退出
                        break
            subprocess.run(["python", os.path.join(path.src, "firewall.py"), str(self.properties.server_port)], check=True)
        except Exception as e:
            logger.error(f"发生错误: {e}")
        finally:
            if process.poll() is None:
                logger.info("强制终止进程")
                process.kill()
            process.stdout.close()
            process.stderr.close()
            process.wait()  # 确保进程已完全退出
            kill_process_on_port(self.properties.server_port)
            logger.info("线程已退出")
            
    def run(self) -> None:
        """运行服务端"""
        pass

if __name__ == "__main__":
    logger.info("开始执行程序")
    _forge = forge.ForgeVersion("1.13.2").latest
    _jdk = jdk.JDK("1.13.2")
    server = Server(_jdk, _forge)
    
    for total, chunk in _forge.download():
        pass

    for total, chunk in _jdk.download():
        pass
    
    for output in server.install():
        logger.info(output)
        
    server.replace()
    
    for output in server.init():
        logger.info(output)
