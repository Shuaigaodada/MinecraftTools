import os
import sys
import path
import tqdm
import argparse
import properties
import subprocess
from forge import ForgeVersion
from jdk import JDK
from loguru import logger
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


if __name__ != "__main__":
    logger.error("请勿直接导入此文件")
    exit(1)

logger.info("开始执行程序")

parser = argparse.ArgumentParser(description="Minecraft 服务端安装程序")
parser.add_argument("--mc", required=True, help="Minecraft 版本")
parser.add_argument("--forge", required=False, help="Forge 版本")
parser.add_argument("--jdk", required=False, help="JDK 路径")

args = parser.parse_args()

logger.info(f"创建目录: {path.server}")
os.makedirs(path.server, exist_ok=True)
jdk = JDK(args.mc)

# 如果 JDK 路径不存在，则下载 JDK
if not args.jdk:
    progress_bar = tqdm.tqdm(desc="下载 JDK", unit="B", unit_scale=True)
    for total_size, downloaded in jdk.download():
        progress_bar.total = total_size
        progress_bar.update(abs(downloaded - progress_bar.n))
    progress_bar.close()
    
    progress_bar = tqdm.tqdm(desc="解压 JDK", unit="B", unit_scale=True)
    for total_size, extracted in jdk.unzip():
        progress_bar.total = total_size
        progress_bar.update(abs(extracted - progress_bar.n))
    progress_bar.close()
else:
    jdk.path = args.jdk

forge = None
# 下载 Forge
if args.forge:
    if args.forge == "latest":
        forge = ForgeVersion(args.mc).latest
    elif args.forge == "recommended":
        forge = ForgeVersion(args.mc).recommended
    else:
        forge = ForgeVersion(args.mc).request_version(args.forge)
else:
    forge = ForgeVersion(args.mc).latest

progress_bar = tqdm.tqdm(desc="下载 Forge", unit="B", unit_scale=True)
for total_size, downloaded in forge.download():
    progress_bar.total = total_size
    progress_bar.update(abs(downloaded - progress_bar.n))
progress_bar.close()

# 创建服务端文件
mcv_path = os.path.join(path.server, forge.minecraft_version)
fgv_path = os.path.join(mcv_path, forge.version)
os.makedirs(fgv_path, exist_ok=True)

# 安装服务端
JDK_PATH = os.path.join(jdk.path, "bin", "java.exe")
try:
    process = subprocess.Popen([
        JDK_PATH,
        "-jar",
        forge.path,
        "--installServer"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=fgv_path)
except FileNotFoundError:
    logger.error(f"未找到 {forge.path} 或 {jdk.path}")
    exit(1)
for line in iter(process.stdout.readline, ''):
    if line:
        logger.info(line.strip())
process.stdout.close()
process.wait()

# 替换文件
_, ver, _ = forge.minecraft_version.split(".")
if int(ver) <= 13:
    bat_prefab = os.path.join(path.prefabs, "1.13-run.bat")
else:
    bat_prefab = os.path.join(path.prefabs, "run.bat")

with open(bat_prefab, "r") as f:
    content = f.read()
content = content.replace("JAVA_PATH", JDK_PATH).replace("FORGE_PATH", os.path.join(path.server, f"forge-{forge.minecraft_version}-{forge.version}.jar"))
bat_path = os.path.join(fgv_path, "run.bat")
with open(bat_path, "w") as f:
    f.write(content)
    
with open(os.path.join(path.prefabs, "eula.txt"), "r") as f:
    content = f.read()
with open(os.path.join(fgv_path, "eula.txt"), "w") as f:
    f.write(content)

logger.info("服务端安装完成")
logger.info(f"服务端路径: {fgv_path}")
logger.info(f"运行服务端: {bat_path}")
try:
    process = subprocess.Popen([
        bat_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=fgv_path)

    for line in iter(process.stdout.readline, ''):
        if line:
            logger.info(line.strip())
            if "Done" in line:
                break
    process.stdout.close()
    process.wait()
finally:
    kill_process_on_port(25565)

logger.info("服务端已关闭")
port = input("请输入服务器端口: ")
logger.info("正在打开服务器端口")

while True:
    try:
        process = subprocess.Popen([
            os.path.join(path.prefabs, "open_port.exe"), 
            port
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in iter(process.stdout.readline, ''):
            if line:
                logger.info(line.strip())
        if process.wait() == 0:
            break
        else:
            logger.error("打开端口失败")
            input("回车键重试(Enter): ")
    except Exception as e:
        logger.error(f"打开端口失败: {e}")
        input("回车键重试(Enter): ")
logger.info(f"{port}端口已打开")