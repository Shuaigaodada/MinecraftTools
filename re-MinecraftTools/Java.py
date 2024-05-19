import json as _json
import config as _config
import requests as _requests
from os.path import join as _join
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Iterable as _Iterable

class JDK:
    def __init__( self, version: _Optional[str] = None ) -> None:
        self.version: _Optional[str] = version
        self.__mapping: _Dict[str, str] = _json.load(
            open(_join(_config.config_path, "url.json" ), "r")
            )
        
    def autoSet( self, version: str ) -> None:
        """自动获取适合MC版本的JDK版本，将JDK.version设置为适合的版本
        
        参数:
            version: MC版本
        """
        vers = int(version.split(".")[1])
        if vers < 17:
            self.version = "8"
        elif vers == 17:
            self.version = "16"
        else:
            self.version = "17"
    
    def download( self, path: str, chunk_size: int = 1024 ) -> _Iterable[tuple[int, int]]:
        """下载JDK
        
        参数:
            path: 下载路径
        
        返回:
            迭代器，每次返回下载进度[总大小, 本次下载大小]
        """
        url = self.__mapping[self.version]["url"]
        with _requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            with open(_join(path, f"jdk-{self.version}.zip"), "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 返回下载进度
                    yield total_size, downloaded
                    

if __name__ == "__main__":
    # test code
    jdk = JDK()
    jdk.autoSet("1.20.1")
    for total, chunk in jdk.download("."):
        print(f"{chunk}/{total}")
    

