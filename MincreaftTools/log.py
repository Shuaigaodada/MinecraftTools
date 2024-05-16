from loguru import logger
import sys
import os

if getattr(sys, "frozen", False):
    basepath = sys._MEIPASS
else:
    basepath = os.path.dirname(os.path.abspath(__file__))
    


logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add(os.path.join(basepath, "logs", "upload.log"), rotation="500 MB")  # Automatically rotate the file when it reaches 500 MB


en_language = {
    "connect": "connecting {0}:{1}...",
    "connect_success": "connect {0}:{1} success! user: {2}",
    "replace_run_bat": "replace run.bat, path: {0}",
    "run_server": "server is running at {0}:{1}",
    "uploading": "{0} uploading file",
    "downloading": "{0} downloading file",
    "upload_success": "{0} upload success!",
    "download_success": "{0} download success!",
    "sending": "sending '{0}' command",
    "send_success": "send '{0}' success!",
    "send_fail": "send '{0}' fail!",
    "load_version": "loading version information...",
    "load_version_success": "load version information success! version: {0}",
    "load_version_fail": "load version information fail, retrying...",
    "generate_headers": "generating headers...",
    "generate_headers_success": "generate headers success! HEADERS: {0}",
    "requesting": "requesting {0}...",
    "request_success": "request '{0}' success!",
    "writing": "writing...",
    "write_success": "write success!",
    "encoding": "encoding for website...",
    "encode_success": "encode success! encoding: {0}",
    "request_fail": "request fail! code status: {0}",
    "parse": "parsing html...",
    "parse_success": "parse webpage success!",
    "filter": "filtering version...",
    "filter_success": "filter version success!",
    "latest": "latest version: {0}",
    "recommended": "recommended version: {0}",
    "set_PATH": "set {0} to PATH",
    "install_forge": "installing forge... path: {0}",
    "waiting_buff_java": "waiting {0}s for server to buffer Java pack...",
    "waiting_buff_forge": "waiting {0}s for server to buffer Forge pack...",
    "jdk_version": "MC {0} is suitable for jdk {1}",
    "generate_dir": "generating directory...",
    "generate_dir_success": "generate directory success!",
    "unziping": "unziping...",
    "unzip_success": "unzip success!",
    "load_url": "loading url mapping...",
    "load_url_success": "load url mapping success!",
    "load_config": "loading config file {0}",
    "load_config_success": "load config file success {0}",
    "install_success": "install {0} success!",
}

cn_language = {
    "connect": "正在连接 {0}:{1}...",
    "connect_success": "连接 {0}:{1} 成功！用户：{2}",
    "replace_run_bat": "替换 run.bat，路径：{0}",
    "run_server": "服务器正在运行于 {0}:{1}",
    "uploading": "{0} 正在上传文件",
    "downloading": "{0} 正在下载文件",
    "upload_success": "{0} 上传成功！",
    "download_success": "{0} 下载成功！",
    "sending": "正在发送 '{0}' 命令",
    "send_success": "发送 '{0}' 成功！",
    "send_fail": "发送 '{0}' 失败！",
    "load_version": "正在加载版本信息...",
    "load_version_success": "加载版本信息成功！版本：{0}",
    "load_version_fail": "加载版本信息失败，正在重试...",
    "generate_headers": "正在生成HEADERS信息...",
    "generate_headers_success": "生成HEADERS信息成功！HEADERS信息：{0}",
    "requesting": "正在请求 {0}...",
    "request_success": "请求 '{0}' 成功！",
    "writing": "正在写入...",
    "write_success": "写入成功！",
    "encoding": "正在为网站编码...",
    "encode_success": "编码成功！编码：{0}",
    "request_fail": "请求失败！状态码：{0}",
    "parse": "正在解析html...",
    "parse_success": "解析网页成功！",
    "filter": "正在过滤版本...",
    "filter_success": "过滤版本成功！",
    "latest": "最新版本：{0}",
    "recommended": "推荐版本：{0}",
    "set_PATH": "设置 {0} 到 PATH",
    "install_forge": "正在安装forge... 路径：{0}",
    "waiting_buff_java": "等待服务器缓冲Java包 {0}秒...",
    "waiting_buff_forge": "等待服务器缓冲Forge包 {0}秒...",
    "jdk_version": "MC {0} 适合 jdk {1}",
    "generate_dir": "正在生成目录...",
    "generate_dir_success": "生成目录成功！",
    "unziping": "正在解压...",
    "unzip_success": "解压成功！",
    "load_url": "正在加载url映射...",
    "load_url_success": "加载url映射成功！",
    "load_config": "正在加载配置文件 {0}",
    "load_config_success": "加载配置文件成功 {0}",
    "install_success": "安装 {0} 成功！",
}

language = cn_language
