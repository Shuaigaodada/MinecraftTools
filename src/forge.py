import requests
from bs4 import BeautifulSoup, Tag
from typing import Tuple, Optional, Iterable

class ForgeVersion:
    URL_FORMAT = "https://maven.minecraftforge.net/net/minecraftforge/forge/{0}-{1}/forge-{2}-{3}-installer.jar"
    def format(minecraft_version: str, version: str) -> str:
        return ForgeVersion.URL_FORMAT.format(minecraft_version, version, minecraft_version, version)
    
    def __init__(self, tag: Tag, minecraft_version: str) -> None:
        self.__tag = tag
        self.__minecraft_version = minecraft_version
        
    @property
    def version(self) -> str:
        return self.__tag.find("td", class_="download-version").text.strip()
    @property
    def url(self) -> str:
        return ForgeVersion.format(self.__minecraft_version, self.version)
    
class Forge:
    def __init__(self, minecraft_version: str) -> None:
        self.mc_version = minecraft_version
        self.__soup: Optional[BeautifulSoup] = None
    
    def __request(self) -> None:
        if self.__soup is not None:
            return
        url = f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{self.mc_version}.html"
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        response.raise_for_status()
        self.__soup = BeautifulSoup(response.text, "lxml")
    
    def all_versions(self) -> Tuple[ForgeVersion, ...]:
        self.__request()
        versions = []
        for ver in self.__soup.find("tbody").find_all("tr"):
            versions.append(ForgeVersion(ver, self.mc_version))
        return tuple(versions)
    
    def request_version(self, version: str) -> ForgeVersion:
        self.__request()
        for ver in self.__soup.find("tbody").find_all("tr"):
            if ver.find("td", class_="download-version").text.strip() == version:
                return ForgeVersion(ver, self.mc_version)
        raise ValueError("未找到指定版本")

    @property
    def latest(self) -> ForgeVersion:
        self.__request()
        version_list = self.__soup.find("tbody")
        return ForgeVersion(version_list.find("tr"), self.mc_version)
    
    @property
    def recommended(self) -> Optional[ForgeVersion]:
        self.__request()
        recommended = self.__soup.find("i", class_="fa promo-recommended")
        if recommended is not None:
            return self.request_version(recommended.parent.find("small").text.split(" - ")[1])
        else:
            return None
        
if __name__ == "__main__":
    forge = Forge("1.20.1")
    print(forge.latest.version)