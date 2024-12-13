import os
import re
import sys
import subprocess
from loguru import logger

def check_admin():
    """检查是否有管理员权限"""
    try:
        subprocess.run("net session", check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def run_as_admin():
    """以管理员权限重新运行脚本"""
    if sys.platform == "win32":
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        try:
            subprocess.run(['powershell', '-Command', f'Start-Process python -ArgumentList "{params}" -Verb RunAs'], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"请求管理员权限失败: {e}")
        sys.exit()

def rule_exists(rule_name):
    """检查防火墙规则是否存在"""
    result = subprocess.run(f'netsh advfirewall firewall show rule name="{rule_name}"', shell=True, capture_output=True, text=True)
    return result.returncode == 0

def open_port(port):
    if not check_admin():
        logger.info("需要管理员权限来创建防火墙规则，正在请求管理员权限...")
        run_as_admin()
        return

    inbound_rule_name = f"Minecraft Server Port {port} Inbound"
    outbound_rule_name = f"Minecraft Server Port {port} Outbound"

    if rule_exists(inbound_rule_name):
        logger.info(f"入站规则已存在: {inbound_rule_name}")
    else:
        try:
            # 允许入站流量通过端口 25565
            subprocess.run(f'netsh advfirewall firewall add rule name="{inbound_rule_name}" dir=in action=allow protocol=TCP localport={port}', shell=True, check=True)
            logger.info(f"成功创建入站防火墙规则: {inbound_rule_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"创建入站防火墙规则失败: {e}")
            return

    if rule_exists(outbound_rule_name):
        logger.info(f"出站规则已存在: {outbound_rule_name}")
    else:
        try:
            # 允许出站流量通过端口 25565
            subprocess.run(f'netsh advfirewall firewall add rule name="{outbound_rule_name}" dir=out action=allow protocol=TCP localport={port}', shell=True, check=True)
            logger.info(f"成功创建出站防火墙规则: {outbound_rule_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"创建出站防火墙规则失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("请提供端口号作为参数")
        sys.exit(1)
    
    port = sys.argv[1]
    open_port(port)
