import os
import path
import npyscreen
import threading
import properties
import subprocess
from jdk import JDK
from loguru import logger
from wcwidth import wcwidth
from forge import ForgeVersion

def kill_process_on_port(port):
    # 查找占用端口的进程 ID
    result = subprocess.run(f'netstat -ano | findstr :{port}', shell=True, capture_output=True, text=True)
    if result.stdout:
        # 提取进程 ID
        lines = result.stdout.strip().split('\n')
        for line in lines:
            parts = line.split()
            pid = parts[-1]
            # 终止进程
            subprocess.run(f'taskkill /PID {pid} /F', shell=True)
            logger.info(f"已终止占用端口 {port} 的进程，PID: {pid}")
    else:
        logger.info(f"没有找到占用端口 {port} 的进程")

def wrap_text(text, width):
    lines = []
    current_line = ""
    current_width = 0

    for char in text:
        char_width = wcwidth(char)
        if char_width < 0:
            char_width = 0  # 处理无法识别的字符
        if current_width + char_width > width:
            lines.append(current_line)
            current_line = char
            current_width = char_width
        else:
            current_line += char
            current_width += char_width
    if current_line:
        lines.append(current_line)
    return lines

if __name__ != "__main__":
    logger.error("请勿直接导入此文件")
    exit(1)

class MainForm(npyscreen.Form):
    def init(self):
        self.minecraft_version = ForgeVersion.all_minecraft_versions()
        self.forge_version = { }
           
    def create(self):
        self.init()
        
        self.mcv_widget = self.add(npyscreen.TitleCombo, name="MC 版本", values=self.minecraft_version)
        self.fgv_widget = self.add(npyscreen.TitleCombo, name="Forge 版本", values=[])
        
        self.download_path = self.add(npyscreen.TitleFilenameCombo, name="下载路径", value=os.path.join(os.getcwd(), "server"))
        self.jdk_widget = self.add(npyscreen.TitleFilenameCombo, name="JDK 路径", value=os.path.join(os.getcwd(), "server", "jdk"))
        
        self.download_button = self.add(npyscreen.ButtonPress, name="下载", when_pressed_function=self.on_download)
        
        self.mcv_widget.when_value_edited = self.update_forge_versions
    
    def update_forge_versions(self):
        # 更新小组件
        self.mcv_widget.update(True)
        self.fgv_widget.update(True)
        self.jdk_widget.update(True)
        self.download_button.update(True)
        try:
            selected_mcv = self.minecraft_version[self.mcv_widget.value]
            
            self.forge_version[selected_mcv] = [forge.version for forge in ForgeVersion(selected_mcv).all_versions()]
            self.forge_version[selected_mcv].insert(0, "latest")
            if ForgeVersion(selected_mcv).recommended:
                self.forge_version[selected_mcv].insert(1, "recommended")
            
            self.fgv_widget.values = self.forge_version[selected_mcv]
            self.fgv_widget.display()
        except TypeError:
            # 此错误代表没有选择 Minecraft 版本 因此不需要处理
            return
    
    def on_download(self):
        self.download_jdk()
        # self.download_forge()
        self.parentApp.setNextForm("LICENSE")
        self.parentApp.switchFormNow()
            
    def download_jdk(self):
        try:
            os.makedirs(path.server, exist_ok=True)
            self.parentApp.jdk = JDK(self.minecraft_version[self.mcv_widget.value])

            if os.path.exists(self.jdk_widget.value):
                self.parentApp.jdk.path = self.jdk_widget.value
            else:
                npyscreen.notify_wait("下载 JDK 中，请稍候...", title="进度", wide=True)
                # 创建一个临时窗口显示进度
                self.progress_form = npyscreen.Form(name="安装进度")
                self.progress_form.add(npyscreen.FixedText, value="下载 JDK 中...", editable=False)
                progress_slider = self.progress_form.add(npyscreen.Slider, 
                                           name="下载进度", 
                                           out_of=100, 
                                           value=0)

                skip_unzip = True
                # 显示下载进度
                if not self.parentApp.jdk.path:
                    for total_size, downloaded in self.parentApp.jdk.download():
                        if total_size > 0:
                            progress_percent = round(downloaded / total_size * 100, 2)
                        else: pass
                        progress_slider.value = progress_percent
                        progress_slider.display()  # 刷新界面
                    skip_unzip = False
                
                # 创建一个临时窗口显示进度
                self.progress_form.add(npyscreen.FixedText, value="解压 JDK 中...", editable=False)
                progress_slider = self.progress_form.add(npyscreen.Slider, 
                                           name="下载进度", 
                                           out_of=100, 
                                           value=0)                
                if not skip_unzip:
                    # npyscreen.notify_wait("解压 JDK 中，请稍候...", title="进度")
                    for total_size, extracted in self.parentApp.jdk.unzip():
                        if total_size > 0:
                            progress_percent = int(extracted / total_size * 100)
                        else: pass
                        progress_slider.value = progress_percent
                        progress_slider.display()  # 刷新界面
                    skip_unzip = False
            # npyscreen.notify_confirm("下载完成！", title="下载状态")
            self.jdk_widget.value = self.parentApp.jdk.path
            self.jdk_widget.display()
            self.download_forge()
        except Exception as e:
            npyscreen.notify_confirm(f"下载失败: {str(e)}", title="下载状态")
            pass
        
        
    
    def download_forge(self):
        try:
            selected_mcv = self.minecraft_version[self.mcv_widget.value]
            selected_fgv = self.forge_version[selected_mcv][self.fgv_widget.value]
            
            if selected_fgv == "latest":
                self.parentApp.forge = ForgeVersion(selected_mcv).latest
            elif selected_fgv == "recommended":
                self.parentApp.forge = ForgeVersion(selected_mcv).recommended
            else:
                self.parentApp.forge = ForgeVersion(selected_mcv).request_version(selected_fgv)
            
            # npyscreen.notify_wait("下载 Forge 中，请稍候...", title="进度")
            
            # 创建一个临时窗口显示进度
            self.progress_form.add(npyscreen.FixedText, value="下载 Forge 中...", editable=False)

            progress_slider = self.progress_form.add(npyscreen.Slider, 
                                        name="下载进度", 
                                        out_of=100, 
                                        value=0)
            
            # 显示下载进度
            for total_size, downloaded in self.parentApp.forge.download():
                progress_percent = round((downloaded / total_size) * 100, 2)
                progress_slider.value = progress_percent
                self.progress_form.display()  # 刷新界面
            
            npyscreen.notify_confirm("下载完成！", title="下载状态", wide=True)
        except Exception as e:
            npyscreen.notify_confirm(f"下载失败: {str(e)}", title="下载状态", wide=True)


class LicenseForm(npyscreen.ActionForm):
    def create(self):
        # 添加标题
        self.add(npyscreen.FixedText, 
                 value="最终用户许可协议 (EULA)", 
                 rely=1, relx=2, 
                 editable=False, 
                 color='STANDOUT')
        
        # 读取并处理许可协议内容
        license_path = os.path.join(path.base, "LicenseAgreement.txt")
        if not os.path.isfile(license_path):
            self.add(npyscreen.FixedText, value="许可协议文件未找到。", rely=3, relx=2, color='DANGER')
            return
        
        with open(license_path, "r", encoding='utf-8') as f:
            content = f.read()
        
        # 获取终端宽度，减去左右边距
        term_width = self.parentApp.getForm("MAIN").max_x - 10  # 根据需要调整
        
        # 使用自定义 wrap_text 函数进行换行
        wrapped_lines = []
        for paragraph in content.split('\n'):
            wrapped = wrap_text(paragraph, width=term_width)
            if wrapped:
                wrapped_lines.extend(wrapped)
            else:
                wrapped_lines.append('')  # 保留空行
        
        # 添加 Pager 控件显示许可协议
        self.eula = self.add(npyscreen.Pager, 
                             name="EULA", 
                             values=wrapped_lines,  # 传递正确换行的行列表
                             relx=2, rely=3, 
                             max_height=-5)
    
    def on_ok(self):
        self.parentApp.switchForm("Install")
        self.parentApp.switchFormNow()
    
    def on_cancel(self):
        # 可以定义取消操作，例如退出程序或返回主菜单
        self.parentApp.switchForm("MAIN")
        
class InstallForm(npyscreen.Form):
    def create(self):
        # 添加标题
        self.add(npyscreen.FixedText, 
                 value="安装输出", 
                 rely=1, relx=2, 
                 editable=False, 
                 color='STANDOUT')
        
        # 添加 Pager 控件显示许可协议
        self.install_output = self.add(npyscreen.Pager, 
                             name="安装输出", 
                             values=[], 
                             relx=2, rely=3, 
                             max_height=-5)
        self.install_button = self.add(npyscreen.ButtonPress, name="安装", when_pressed_function=self.start_install)
    
    def start_install(self):
        # 启动安装过程的线程
        install_thread = threading.Thread(target=self.install, daemon=True)
        install_thread.start()

    def install(self):
        mcv_path = os.path.join(path.server, self.parentApp.forge.minecraft_version)
        fgv_path = os.path.join(mcv_path, self.parentApp.forge.version)
        os.makedirs(fgv_path, exist_ok=True)
        
        JDK_PATH = os.path.join(self.parentApp.jdk.path, "bin", "java.exe")
        try:
            process = subprocess.Popen([
                JDK_PATH,
                "-jar",
                self.parentApp.forge.path,
                "--installServer"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=fgv_path)
        except FileNotFoundError:
            logger.error(f"未找到 {self.parentApp.forge.path} 或 {self.parentApp.jdk.path}")
            exit(1)
        for line in iter(process.stdout.readline, ''):
            if line:
                clean_line = line.strip()
                # 使用 async_call 将更新操作提交给主线程
                self.parentApp.event_queue.put(lambda: self.update_install_output(clean_line))
                
        process.stdout.close()
        process.wait()
        self.parentApp.event_queue.put(lambda: npyscreen.notify_confirm("安装完成！", title="安装状态", wide=True))
    
    def update_install_output(self, line):
        self.install_output.values.append(line)
        # 计算新的 start_line 以滚动到最底端
        total_lines = len(self.install_output.values)
        pager_height = self.install_output.height
        new_start = max(total_lines - pager_height, 0)
        self.install_output.start_line = new_start
        #  刷新 Pager 显示
        self.install_output.display()

class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.forge = None
        self.jdk = None
        self.addForm("MAIN", MainForm, name="Minecraft 服务端安装程序")
        self.addForm("LICENSE", LicenseForm, name="最终用户许可协议")
        self.addForm("Install", InstallForm, name="安装输出")

app = App()
app.run()

# # 创建服务端文件
# mcv_path = os.path.join(path.server, forge.minecraft_version)
# fgv_path = os.path.join(mcv_path, forge.version)
# os.makedirs(fgv_path, exist_ok=True)

# # 安装服务端
# JDK_PATH = os.path.join(jdk.path, "bin", "java.exe")
# try:
#     process = subprocess.Popen([
#         JDK_PATH,
#         "-jar",
#         forge.path,
#         "--installServer"
#     ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=fgv_path)
# except FileNotFoundError:
#     logger.error(f"未找到 {forge.path} 或 {jdk.path}")
#     exit(1)
# for line in iter(process.stdout.readline, ''):
#     if line:
#         logger.info(line.strip())
# process.stdout.close()
# process.wait()

# # 替换文件
# _, ver, _ = forge.minecraft_version.split(".")
# if int(ver) <= 13:
#     bat_prefab = os.path.join(path.prefabs, "1.13-run.bat")
# else:
#     bat_prefab = os.path.join(path.prefabs, "run.bat")

# with open(bat_prefab, "r") as f:
#     content = f.read()
# content = content.replace("JAVA_PATH", JDK_PATH).replace("FORGE_PATH", os.path.join(path.server, f"forge-{forge.minecraft_version}-{forge.version}.jar"))
# bat_path = os.path.join(fgv_path, "run.bat")
# with open(bat_path, "w") as f:
#     f.write(content)
    
# with open(os.path.join(path.prefabs, "eula.txt"), "r") as f:
#     content = f.read()
# with open(os.path.join(fgv_path, "eula.txt"), "w") as f:
#     f.write(content)

# logger.info("服务端安装完成")
# logger.info(f"服务端路径: {fgv_path}")
# logger.info(f"运行服务端: {bat_path}")
# try:
#     process = subprocess.Popen([
#         bat_path
#     ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=fgv_path)

#     for line in iter(process.stdout.readline, ''):
#         if line:
#             logger.info(line.strip())
#             if "Done" in line:
#                 break
#     process.stdout.close()
#     process.wait()
# finally:
#     kill_process_on_port(25565)

# logger.info("服务端已关闭")
# port = input("请输入服务器端口: ")
# logger.info("正在打开服务器端口")

# while True:
#     try:
#         process = subprocess.Popen([
#             os.path.join(path.prefabs, "open_port.exe"), 
#             port
#         ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         for line in iter(process.stdout.readline, ''):
#             if line:
#                 logger.info(line.strip())
#         if process.wait() == 0:
#             break
#         else:
#             logger.error("打开端口失败")
#             input("回车键重试(Enter): ")
#     except Exception as e:
#         logger.error(f"打开端口失败: {e}")
#         input("回车键重试(Enter): ")
# logger.info(f"{port}端口已打开")