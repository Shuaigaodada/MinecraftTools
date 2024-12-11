import os
import jdk
import forge
import subprocess
import platform
from loguru import logger

def install_server(jdk: jdk.JDK, forge: forge.Forge, path: str):
    """安装服务端
    
    Args:
        jdk: JDK实例
        forge: Forge实例
        path: 安装路径
    """
    logger.info(f"执行 mkdir -p {path}")
    # 创建目录
    os.makedirs(path, exist_ok=True)
    
    if jdk.path is None:
        print("请先下载JDK")
        return
    if forge.path is None:
        print("请先下载Forge")
        return
    
    java_executable = "java.exe" if platform.system() == "Windows" else "java"
    java_path = os.path.join(jdk.path, "bin", java_executable)
    
    logger.info(f"执行 {java_path} -jar {forge.path} --installServer --target {path}")
    process = subprocess.Popen([
        java_path,
        "-jar",
        forge.path,
        "--installServer",
        "--target",
        path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    for line in iter(process.stdout.readline, ''):
        if line:
            print(line.strip())
            yield line.strip()
    
    process.stdout.close()
    process.wait()

if __name__ == "__main__":
    logger.info("开始执行程序")
    _forge = forge.ForgeVersion("1.20.1").recommended
    _jdk = jdk.JDK("1.20.1")
    
    for total, chunk in _forge.download("./temp"):
        print(f"{chunk}/{total}")
    
    for output in install_server(_jdk, _forge, "./server"):
        print(output)
    logger.info("程序执行完毕")