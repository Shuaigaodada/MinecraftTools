import os
import path
import json
import time
import zipfile
import requests
from loguru import logger
from typing import Dict, Optional, Iterable

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
        # logger.info(f"自动获取适合MC版本的JDK版本, 当前MC版本: {minecraft_version}")
        vers = int(minecraft_version.split(".")[1])
        if vers < 17:
            self.version = "8"
        elif vers == 17:
            self.version = "16"
        else:
            self.version = "17"

    def is_downloaded(self) -> bool:
        """检查JDK是否已经下载
        
        Returns:
            bool: 是否已经下载
        """
        return os.path.exists(f"{path.server}/jdk-{self.version}")
    
    def download(self, chunk_size: int = 102400) -> Iterable[tuple[int, int]]:
        """下载JDK
        
        参数:
            path: 下载路径
        
        返回:
            迭代器，每次返回下载进度[总大小, 本次下载大小]
        """
        if self.is_downloaded():
            # logger.info("JDK已下载")
            self.path = f"{path.server}/jdk-{self.version}"
            return
        url = self.url_mapping[self.version]["url"]
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            with open(f"{path.server}/jdk-{self.version}.zip", "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 返回下载进度
                    yield total_size, downloaded

            self.path = f"{path.server}/jdk-{self.version}"
    
    def unzip(self):
        zip_path = f"{path.server}/jdk-{self.version}.zip"
        extract_path = f"{path.server}"
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            total_size = sum(file.file_size for file in zip_ref.infolist())
            extracted_size = 0
            for file in zip_ref.infolist():
                zip_ref.extract(file, extract_path)
                extracted_size += file.file_size
                yield total_size, extracted_size
        # 删除zip文件    
        os.remove(f"{path.server}/jdk-{self.version}.zip")
        if self.version == "8":
            src = f"{path.server}/openlogic-openjdk-8u412-b08-windows-64"
            dst = f"{path.server}/jdk-{self.version}"
            
            # 检查源目录是否存在
            if not os.path.exists(src):
                logger.error(f"源目录不存在: {src}")
            # 检查目标目录是否已经存在
            elif os.path.exists(dst):
                logger.error(f"目标目录已存在: {dst}")
            else:
                try:
                    os.rename(src, dst)
                except PermissionError as e:
                    logger.error(f"权限错误: {e}")
                    # 检查文件权限
                    if not os.access(src, os.W_OK):
                        logger.error(f"没有写权限: {src}")
                    if not os.access(dst, os.W_OK):
                        logger.error(f"没有写权限: {dst}")
                    time.sleep(1)
                    os.rename(src, dst)


if __name__ == "__main__":
    # test code
    jdk = JDK("1.20.1")
    for total, chunk in jdk.download(409600):
        print(f"{chunk}/{total}")
