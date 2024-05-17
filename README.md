# MinecraftTools
一个MC工具包，用于快速远程开启服务器和在本地开启服务器进行联机

# 服务器功能
该功能要求电脑内必须拥有ssh和连接密钥(如果没有请省略)，
确保您可以在您的电脑端能过连接服务器，
软件将通过ssh在您的服务端进行安装MC的服务端代码。

#### 功能1: 自动安装Forge Server
在`GUI`界面中选择对应 `MC版本` 的 Forge，
并选择 `最新版本` or `稳定版本`(默认为`稳定版本`)，
完成选择后，程序通过`scp`(暂定)将文件下载并传输至服务器，
此时 GUI 界面则是会显示`在服务器安装`按钮，点击后，
程序将自动发送指令在服务端安装 Forge Server，指令请查看这: [点我查看](#安装forge-server)













# 使用指令
##### 安装Forge Server
使用以下指令来安装服务端，无GUI，检测系统版本，如果版本不为`windows`
则使用 `apt` 包
```bash
# windows
java -version # 如果返回错误则使用scp传输java
java -jar forge-mc_version-forge_version.jar -installServer
# linux
chmod +x ./install_java.sh
./install_java.sh
java -jar forge-mc_version-forge_version.jar -installServer
```
sh文件
```sh
java -version
if [ "$?" -ne 0 ]; then
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y openjdk-version-jdk
fi
```

安装完成后，会自动运行一次服务器以创建文件
```bash
chmod +x ./run.sh
./run.sh
```
自动将 `eula` 设置为 `true`
