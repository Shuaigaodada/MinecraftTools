import os
import json
import zipfile
import requests
from loguru import logger
from typing import Dict, Optional, Iterable

basepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "server")


class JDK:
    def __init__(self, minecraft_version: str) -> None:
        self.version: Optional[str] = None
        with open("configs/url.json", "r") as f:
            self.url_mapping: Dict[str, str] = json.load(f)
        self.auto_set(minecraft_version)
        
        self.path = None
    
    def auto_set(self, minecraft_version: str) -> None:
        """自动获取适合MC版本的JDK版本, 并将JDK.version设置为合适的版本
        
        Args:
            minecraft_version: 我的世界版本
        """
        logger.info(f"自动获取适合MC版本的JDK版本, 当前MC版本: {minecraft_version}")
        vers = int(minecraft_version.split(".")[1])
        if vers < 17:
            self.version = "8"
        elif vers == 17:
            self.version = "16"
        else:
            self.version = "17"

    def download(self, chunk_size: int = 102400) -> Iterable[tuple[int, int]]:
        """下载JDK
        
        参数:
            path: 下载路径
        
        返回:
            迭代器，每次返回下载进度[总大小, 本次下载大小]
        """
        url = self.url_mapping[self.version]["url"]
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            with open(f"{basepath}/jdk-{self.version}.zip", "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 返回下载进度
                    yield total_size, downloaded
            
            logger.info("下载完成，正在解压")
            with zipfile.ZipFile(f"{basepath}/jdk-{self.version}.zip", "r") as zip_ref:
                zip_ref.extractall(f"{basepath}")
            logger.info("解压完成 删除zip文件")
            # 删除zip文件    
            os.remove(f"{basepath}/jdk-{self.version}.zip")
            if self.version == "8":
                src = f"{basepath}/openlogic-openjdk-8u412-b08-windows-64"
                dst = f"{basepath}/jdk-{self.version}"
                
                # 检查源目录是否存在
                if not os.path.exists(src):
                    logger.error(f"源目录不存在: {src}")
                # 检查目标目录是否已经存在
                elif os.path.exists(dst):
                    logger.error(f"目标目录已存在: {dst}")
                else:
                    try:
                        os.rename(src, dst)
                        logger.info(f"重命名成功: {src} -> {dst}")
                    except PermissionError as e:
                        logger.error(f"权限错误: {e}")
                        # 检查文件权限
                        if not os.access(src, os.W_OK):
                            logger.error(f"没有写权限: {src}")
                        if not os.access(dst, os.W_OK):
                            logger.error(f"没有写权限: {dst}")
                        raise e
                    
            self.path = f"{basepath}/jdk-{self.version}"


if __name__ == "__main__":
    # test code
    jdk = JDK("1.20.1")
    for total, chunk in jdk.download(409600):
        print(f"{chunk}/{total}")
