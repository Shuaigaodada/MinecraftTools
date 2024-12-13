import os
import requests
from loguru import logger
from bs4 import BeautifulSoup, Tag
from typing import Tuple, Optional, Iterable

basepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "server")

class Forge:
    URL_FORMAT = "https://maven.minecraftforge.net/net/minecraftforge/forge/{0}-{1}/forge-{2}-{3}-installer.jar"
    def format(minecraft_version: str, version: str) -> str:
        return Forge.URL_FORMAT.format(minecraft_version, version, minecraft_version, version)
    
    def __init__(self, tag: Tag, minecraft_version: str) -> None:
        self.__tag = tag
        self.minecraft_version = minecraft_version
        self.path = None
        
    @property
    def version(self) -> str:
        logger.info("查找td标签, class=download-version")
        return self.__tag.find("td", class_="download-version").text.strip()
    @property
    def url(self) -> str:
        logger.info("生成下载链接")
        return Forge.format(self.minecraft_version, self.version)
    
    def download(self, chunk_size: int = 102400) -> Iterable[tuple[int, int]]:
        """下载Forge
        参数:
            path: 下载路径
            chunk_size: 下载块大小
        返回:
            迭代器，每次返回下载进度[总大小, 本次下载大小]
        """
        if os.path.exists(f"{basepath}/{self.minecraft_version}/{self.version}"):
            logger.info(f"Forge {self.version} 已下载")
            self.path = f"{basepath}/{self.minecraft_version}/{self.version}"
            return
        logger.info(f"下载Forge: {self.version}")
        with requests.get(self.url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            with open(f"{basepath}/forge-{self.version}.jar", "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 返回下载进度
                    yield total_size, downloaded
        logger.info(f"下载完成, 保存路径: {basepath}/forge-{self.version}.jar")
        self.path = f"{basepath}/forge-{self.version}.jar"
    
    
class ForgeVersion:
    def __init__(self, minecraft_version: str) -> None:
        self.mc_version = minecraft_version
        self.__soup: Optional[BeautifulSoup] = None
    
    def __request(self) -> None:
        if self.__soup is not None:
            return

        url = f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{self.mc_version}.html"
        
        logger.info(f"请求: {url}")
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        response.raise_for_status()
        
        logger.info(f"请求成功, 状态码: {response.status_code}")
        self.__soup = BeautifulSoup(response.text, "lxml")
        logger.info("解析成功, 使用lxml解析器")
    
    def all_versions(self) -> Tuple[Forge, ...]:
        self.__request()
        versions = []
        for ver in self.__soup.find("tbody").find_all("tr"):
            versions.append(Forge(ver, self.mc_version))
        return tuple(versions)
    
    def request_version(self, version: str) -> Forge:
        self.__request()
        for ver in self.__soup.find("tbody").find_all("tr"):
            if ver.find("td", class_="download-version").text.strip() == version:
                return Forge(ver, self.mc_version)
        raise ValueError("未找到指定版本")

    @property
    def latest(self) -> Forge:
        self.__request()
        version_list = self.__soup.find("tbody")
        return Forge(version_list.find("tr"), self.mc_version)
    
    @property
    def recommended(self) -> Optional[Forge]:
        self.__request()
        recommended = self.__soup.find("i", class_="fa promo-recommended")
        if recommended is not None:
            return self.request_version(recommended.parent.find("small").text.split(" - ")[1])
        else:
            logger.error("未找到推荐版本")
            return None
        
if __name__ == "__main__":
    forge = ForgeVersion("1.20.1")
    for total, chunk in forge.recommended.download(".", 102400):
        print(f"{chunk}/{total}")
    print(forge.recommended.version)