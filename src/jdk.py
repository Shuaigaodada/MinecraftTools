import os
import json
import zipfile
import requests
from typing import Dict, Optional, Iterable

class JDK:
    def __init__(self, minecraft_version: str) -> None:
        self.version: Optional[str] = None
        with open("configs/url.json", "r") as f:
            self.url_mapping: Dict[str, str] = json.load(f)
        self.auto_set(minecraft_version)
    
    def auto_set(self, minecraft_version: str) -> None:
        """自动获取适合MC版本的JDK版本, 并将JDK.version设置为合适的版本
        
        Args:
            minecraft_version: 我的世界版本
        """
        vers = int(minecraft_version.split(".")[1])
        if vers < 17:
            self.version = "8"
        elif vers == 17:
            self.version = "16"
        else:
            self.version = "17"

    def download(self, path: str, chunk_size: int = 1024) -> Iterable[tuple[int, int]]:
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
            with open(f"{path}/jdk-{self.version}.zip", "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 返回下载进度
                    yield total_size, downloaded
            
            with zipfile.ZipFile(f"{path}/jdk-{self.version}.zip", "r") as zip_ref:
                zip_ref.extractall(f"{path}")
            # 删除zip文件    
            os.remove(f"{path}/jdk-{self.version}.zip")


if __name__ == "__main__":
    # test code
    jdk = JDK("1.20.1")
    for total, chunk in jdk.download(".", 409600):
        print(f"{chunk}/{total}")
