import os as _os
import requests as _requests
from bs4 import BeautifulSoup as _BS
from bs4 import Tag as _Tag
from typing import Tuple as _Tuple
from typing import Optional as _Optional
from typing import Iterable as _Iterable


class VersionInfo:
    def __init__(self, tag: _Tag, MCV: str) -> None:
        self.__tag = tag
        self.__MCV = MCV
    
    @property
    def version( self ) -> str:
        return self.__tag.find("td", class_="download-version").text.strip()
    
    @property
    def url( self ) -> str:
        return \
f"https://maven.minecraftforge.net/net/minecraftforge/forge/{self.__MCV}-{self.version}/forge-{self.__MCV}-{self.version}-installer.jar"
    
    def __eq__( self, other ) -> bool:
        return self.version == other.version

    def __str__(self) -> str:
        return self.version
    def __repr__(self) -> str:
        return self.version

    def download( self, path: str ) -> _Iterable[_Tuple[int, int]]:
        """下载Forge"""
        with _requests.get(self.url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            with open(_os.path.join(path, f"forge-{self.__MCV}-{self.version}-installer.jar"), "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
                    downloaded += len(chunk)
                    yield total_size, downloaded

class Forge:
    def __init__( self, __MCV: _Optional[str] ) -> None:
        self.__MCV: _Optional[str] = __MCV
        self.__soup: _Optional[_BS] = None
    
    def setMCV( self, __MCV: str ) -> None:
        """设置MC版本"""
        self.__MCV = __MCV
    
    def __request( self ) -> None:
        """请求版本网页"""
        if self.__MCV is None:
            raise ValueError("MC版本未设置")
        if self.__soup is not None:
            return
        url: str = "https://files.minecraftforge.net/net/minecraftforge/forge/index_{0}.html"
        url = url.format( self.__MCV )
        response = _requests.get( url )
        response.encoding = response.apparent_encoding
        self.__soup = _BS( response.text, "lxml" )
        
    def requestAllVersions( self ) -> _Tuple[VersionInfo, ...]:
        """请求该版本的所有Forge版本"""
        self.__request()
        version_list = self.__soup.find("tbody")
        versions = []
        for ver in version_list.find_all("tr"):
            versions.append( VersionInfo(ver, self.__MCV) )
        return versions
    
    @property
    def latest( self ) -> VersionInfo:
        """请求最新的Forge版本"""
        self.__request()
        version_list = self.__soup.find("tbody")
        return VersionInfo(version_list.find("tr"), self.__MCV)

    @property
    def recommended( self ) -> VersionInfo:
        """请求推荐的Forge版本"""
        self.__request()
        recommended = self.__soup.find("i", class_="fa promo-recommended")
        if recommended is not None:
            return self.requestVersion( recommended.parent.find("small").text.split(" - ")[1] )
        else:
            return None
        
    def requestVersion(self, version: str) -> VersionInfo:
        """请求指定版本的Forge版本"""
        self.__request()
        version_list = self.__soup.find("tbody")
        for ver in version_list.find_all("tr"):
            if ver.find("td", class_="download-version").text.strip() == version:
                return VersionInfo(ver, self.__MCV)
        raise ValueError("未找到指定版本")
        
        
        


if __name__ == "__main__":
    forge = Forge("1.20.1")
    vers = forge.requestAllVersions()
    print(vers)
    # for total, chunk in forge.latest.download("."):
    #     print(f"{chunk}/{total}")