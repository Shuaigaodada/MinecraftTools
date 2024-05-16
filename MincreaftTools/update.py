from git import Repo, InvalidGitRepositoryError
import requests
import time
from fake_headers import Headers
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from os.path import join, dirname, abspath
import sys

url: str = None
url_mapping: dict = {
    "github": "https://github.com/Shuaigaodada/MincreaftTools.git"
}

def __test_connection(__url: str) -> float:
    start_time = time.time()
    header = Headers("chrome", "win", True).generate()
    try:
        respones = requests.get(__url, headers=header, timeout=5)
        respones.raise_for_status()
    except requests.exceptions.RequestException:
        return 9999
    return time.time() - start_time

def ping() -> None:
    global url
    logger.info("开始测试github和gitee的连接速度")
    with ThreadPoolExecutor(max_workers=2) as excutor:
        github_future = excutor.submit(__test_connection, "https://github.com")
        gitee_future = excutor.submit(__test_connection, "https://gitee.com")
    
    gitee_speed = gitee_future.result()
    github_speed = github_future.result()
    logger.info(f"测试完成!\ngithub: {round(github_speed * 1000)}ms\ngitee: {round(gitee_speed * 1000)}ms")
    if gitee_speed < github_speed:
        url = "gitee"
    else:
        url = "github"


def update():
    if getattr(sys, "frozen", False):
        basepath = sys._MEIPASS
    else:
        basepath = dirname(abspath(__file__))
    
    try:    
        repo = Repo(basepath)
    except InvalidGitRepositoryError:
        repo = Repo.init(basepath)
        repo.create_remote("origin", url_mapping[url])
    windows = repo.remote("origin")
    windows.pull("windows-build")
    