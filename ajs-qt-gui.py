import sys
import subprocess
import os
import signal
import json
import math
import time
import re
import platform
try:
    import aiohttp
except ImportError:
    print("aiohttp not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp","-i","https://pypi.tuna.tsinghua.edu.cn/simple"])
    print("aiohttp installed successfully.")
try:
    import requests
except ImportError:
    print("requests not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests","-i","https://pypi.tuna.tsinghua.edu.cn/simple"])
    print("requests installed successfully.")

try:
    import PyQt5
except ImportError:
    print("PyQt5 not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5","-i","https://pypi.tuna.tsinghua.edu.cn/simple"])
    print("PyQt5 installed successfully.")

try:
    import dotenv
except ImportError:
    print("dotenv not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv","-i","https://pypi.tuna.tsinghua.edu.cn/simple"])
    print("dotenv installed successfully.")

import requests
import asyncio
import aiohttp
import dotenv
from dotenv import load_dotenv
from PyQt5.QtWidgets import QComboBox, QApplication, QCheckBox, QGridLayout, QMessageBox, QTextEdit, QScrollArea, \
    QFileDialog, QLineEdit, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QTextOption, QTextCursor, QPixmap, QImage
from PyQt5 import QtWidgets

DEBUG = 1

uienvPath = "./.uienv"

class Util:
    @staticmethod
    def count_files_with_regex(directory, pattern):
        count = 0
        regex = re.compile(pattern)
        for file in os.listdir(directory):
            if regex.search(file):
                count += 1
        return count
    
    @staticmethod
    def debugPrint(s):
        if DEBUG:
            print(s)
    
    @staticmethod
    def loadUIEnv():
        proxy_url_list = ["https://ep.atomicals.xyz/proxy/", "https://ep.nextdao.xyz/proxy/"]
        if not os.path.exists(".uienv"):
            Util.debugPrint("创建.uienv文件")
            # create .uienv file
            with open(uienvPath, "w") as f:
                f.write("AJS_PATH=./")
                f.write(f"\nPROXY_URLS={','.join(proxy_url_list)}")
            Util.debugPrint(".uienv文件创建完成")
        
        load_dotenv(dotenv_path=".uienv", verbose=True)
        Util.debugPrint(os.environ.get("PROXY_URLS"))
        Util.debugPrint(".uienv文件加载完成")
    
    @staticmethod
    def loadAJSEnv():
        try:
            ajsPath = os.environ["AJS_PATH"]
            if os.path.exists(os.path.join(ajsPath, ".env")):
                load_dotenv(dotenv_path=os.path.join(ajsPath, ".env"), verbose=True)
                Util.debugPrint(".env文件加载完成")
                ajsEnvPath = os.path.join(ajsPath, ".env")
                Util.debugPrint(ajsEnvPath)
            else:
                Util.debugPrint("找不到.env文件，请在 <设置> 菜单指定 atomicals-js 路径.")
                QMessageBox.warning(None, "警告", "找不到.env文件，请在 <设置> 菜单指定 atomicals-js 路径.")
        except Exception as e:
            Util.debugPrint(f"error: {e}")
    
    @staticmethod
    def saveEnv(envFilePath, key, value):
        if os.path.exists(envFilePath):
            dotenv.set_key(envFilePath, key, value)
    
    @staticmethod
    def getImportedWalletList():
        walletList = []
        try:
            walletPath = os.environ["WALLET_PATH"]
        
            if walletPath.startswith("./"):
                walletPath = os.environ["WALLET_PATH"][2:]
            fullWalletFilePath = os.path.join(os.environ["AJS_PATH"], walletPath, os.environ["WALLET_FILE"])
            Util.debugPrint(fullWalletFilePath)
            with open(fullWalletFilePath, "r") as f:
                walletJson = json.load(f)
            if walletJson["imported"]:
                for key in walletJson["imported"]:
                    walletList.append(key)
        
        except KeyError as e:
            Util.debugPrint(f"error: {e}")
        
        return walletList

    @staticmethod
    def ansiToHtml(text):
        # 转换空格为HTML空格实体
        text = text.replace(' ', '&nbsp;')
        text = text.replace('\n', '<br>')

        # 转换ANSI转义序列到HTML
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        text = ansi_escape.sub(lambda match: Util.convertAnsiToHtml(match.group()), text)

        # 使用<pre>标签来保持文本格式
        return f'<pre>{text}</pre>'

    @staticmethod
    def convertAnsiToHtml(ansi_sequence):
        # 定义 ANSI 到 HTML 的转换
        ansi_to_html = {
            '\x1b[0m': '</span>',  # 重置
            '\x1b[47m': '<span style="background-color:#ffffff;">',  # 白色背景
            '\x1b[40m': '<span style="background-color:#000000;">',  # 黑色背景
            # 可以继续添加其他 ANSI 序列的转换
        }
        return ansi_to_html.get(ansi_sequence, '')

# 定义一个信号处理函数
def signal_handler(signum, frame):
    QApplication.quit()


class GasPriceThread(QThread):
    def __init__(self):
        super().__init__()
        self.gasPriceDisplay = None
        self.feeRateEdit = None
        self.logDisplay = None
        self.running = True

    def setUI(self,gasPriceDisplay,feeRateEdit,logDisplay):
        self.gasPriceDisplay = gasPriceDisplay
        self.feeRateEdit = feeRateEdit
        self.logDisplay = logDisplay

    def run(self):
        tryCount = 3
        while tryCount > 0 and self.running:
            try:
                response = requests.get("https://mempool.space/api/v1/fees/recommended")
                if response.status_code == 200:
                    gasPrice = response.json()["fastestFee"]
                    self.gasPriceDisplay.setText(f"当前 gas 价格: {gasPrice} sats/vB")
                    self.feeRateEdit.setText(str(gasPrice))
                    self.logDisplay.append(f"当前 gas 价格: {gasPrice} sats/vB")
                    break
                else:
                    self.logDisplay.append(f"获取 gas 价格失败，状态码: {response.status_code}")
            except Exception as e:
                self.logDisplay.append(f"获取 gas 价格时发生错误: {e}")
            tryCount -= 1

    def stop(self):
        self.running = False

class GetContainerItemStatusThread(QThread):
    updateStatusSingal = pyqtSignal(QLabel, str)

    async def checkContainerItemByUrlRequest(self, url, session, containerName, itemName):
        headers = {'Content-Type': 'application/json'}
        data = {"params": [containerName, itemName]}
        retry_count = 5
        while retry_count > 0:
            try:
                # print({"url": url,"data":data})
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        # print("http ok:",data)
                        return await response.json()
                    else:
                        # print("http error:",data)
                        retry_count -= 1
            except Exception as e:
                retry_count -= 1
                print(e)
        return {"error": "error"}

    def __init__(self, images, folder_path, text_labels):
        super().__init__()
        self.images = images
        self.folder_path = folder_path
        self.text_labels = text_labels
        self.isRunning = True
        self.loop = None

    async def getStatus(self, session, i, pic):
        containerName = self.folder_path.split("/")[-1]
        fileName = pic["filename"]
        pattern = r'item-(\d+)\.json'
        match = re.search(pattern, fileName)
        urls = [website + "blockchain.atomicals.get_by_container_item" for website in ["https://ep.atomicals.xyz/proxy/", "https://ep.nextdao.xyz/proxy/"]]
        try:
            urls = os.environ.get("PROXY_URLS").split(",")
            urls = [website + "blockchain.atomicals.get_by_container_item" for website in urls]
        except Exception as e:
            Util.debugPrint(e)

        if match:
            fileName = match.group(1)
            response = await self.checkContainerItemByUrlRequest(urls[i % len(urls)], session, containerName, fileName)
            # Util.debugPrint(response)
            if response:
                new_text = self.text_labels[i].text()
                # print(response)
                if "response" in response:
                    if response.get("response", {}).get("result", {}).get("status") is None:
                        new_text += "✅"
                    else:
                        new_text += "❌"
                    self.text_labels[i].setText(new_text)
                    # self.updateStatusSingal.emit(self.text_labels[i],new_text)
                elif "error" in response and response.get("error") == "timeout":
                    new_text = self.text_labels[i].text() + "⌛"
                    self.text_labels[i].setText(new_text)
            else:
                new_text = self.text_labels[i].text() + "❓"
                self.text_labels[i].setText(new_text)
        else:
            print("didn't match")

    async def createTasks(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, pic in enumerate(self.images):
                if not self.isRunning:
                    break
                tasks.append(asyncio.create_task(self.getStatus(session, i, pic)))
            await asyncio.wait(tasks)

    def run(self):
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError as e:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.createTasks())
        except asyncio.exceptions.CancelledError:
            Util.debugPrint("cancelled")
            self.loop.close()

    def stop(self):
        self.isRunning = False

        # 取消所有未完成的异步任务
        if self.loop:
            for task in asyncio.all_tasks(self.loop):
                task.cancel()


class CommandThread(QThread):
    newOutput = pyqtSignal(str)
    finishedOutput = pyqtSignal(str)

    def __init__(self, command, count=1):
        super().__init__()
        self.command = command
        self.process = None
        self.count = count  # 运行次数
        self.output = ""  # 存储累积的输出

    def runner(self):
        try:
            if os.name != 'nt':  # 非 Windows 系统
                self.process = subprocess.Popen(self.command, cwd=os.environ["AJS_PATH"], stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT, shell=True, text=True, bufsize=1,
                                                preexec_fn=os.setsid)
            else:  # Windows 系统
                self.process = subprocess.Popen(self.command, cwd=os.environ["AJS_PATH"], stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT, shell=True, text=True, bufsize=1)
            for line in iter(self.process.stdout.readline, ''):
                self.newOutput.emit(line)
                time.sleep(0.001)
                # self.output += line
            # self.finishedOutput.emit(self.output)
        except Exception as e:
            print(f"error: {e}")
            return


    def run(self):
        for i in range(self.count):
            self.runner()

    def stop(self):
        try:
            if self.process:
                if os.name != 'nt':  # 非 Windows 系统
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:  # Windows 系统
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
                    Util.debugPrint(" force killed")
        except Exception as e:
            Util.debugPrint(e)

        self.process = None


class AtomicalToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        Util.loadUIEnv()
        Util.loadAJSEnv()
        self.commandThreads = []
        self.itemStatusThreads = []
        self.gasPriceThread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Atomicals-JS Qt GUI')
        self.setGeometry(200, 200, 1450, 750)
        self.setMinimumSize(1250, 700)  # 设置最小大小
        # self.setMaximumSize(1450, 750)  # 设置最大大小
        # 创建主布局
        mainLayout = QHBoxLayout()

        # 创建左侧菜单
        self.menuWidget = QWidget()
        self.menuWidget.setMaximumHeight(750)
        menuLayout = QVBoxLayout(self.menuWidget)

        self.addMenuLabel(menuLayout, "钱包")
        self.addButton(menuLayout, "初始化主钱包", self.openWalletInitTab)
        self.addButton(menuLayout, "导入钱包", self.openImportWalletTab)
        self.addButton(menuLayout, "查看钱包地址", self.openDisplayWalletTab)
        self.addButton(menuLayout, "主钱包详细信息", self.openMainWalletDetailsTab)
        self.addButton(menuLayout, "导入钱包详细信息", self.openImportedWalletDetailsTab)

        # self.addButton(menuLayout, "使用助记词导出私钥", self.openExportPrivateKeyTab)
        # self.addButton(menuLayout, "获取地址信息", self.openAddressInfoTab)
        self.addButton(menuLayout, "设置", self.openSettingsTab)
        self.addMenuLabel(menuLayout, "Mint Atomicals")
        self.addButton(menuLayout, "mint Realm/SubRealm", self.openMintRealmTab)
        self.addButton(menuLayout, "mint NFT", self.openMintNftTab)
        self.addButton(menuLayout, "mint FT（ARC20）", self.openMintDFTTab)
        self.addButton(menuLayout, "mint Container Item", self.openMintContainerItemTab)

        self.addMenuLabel(menuLayout, "工具")
        self.addButton(menuLayout, "查询领域/子领域信息", self.openRealmInfoTab)
        self.addButton(menuLayout, "解析 Container Item Images", self.openContainerItemImagesTab)

        self.addMenuLabel(menuLayout, "帮助")
        self.addButton(menuLayout, "CLI 版本号", self.openCLIversionTab)
        self.addButton(menuLayout, "显示命令帮助", self.openCLIhelpTab)
        self.addButton(menuLayout, "服务器版本信息", self.openServerVersionTab)
        self.addButton(menuLayout, "关于", self.openAboutTab)
        self.addButton(menuLayout, "退出", self.closeApp)

        # 添加 Tab Widget
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)

        # 设置主布局
        mainLayout.addWidget(self.menuWidget, 1)
        mainLayout.addWidget(self.tabWidget, 5)
        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def closeApp(self):
        if len(self.commandThreads)!=0:
            for thread in self.commandThreads:
                thread.stop()

        if len(self.itemStatusThreads)!=0:
            for thread in self.itemStatusThreads:
                thread.stop()

        if self.gasPriceThread and self.gasPriceThread.isRunning():
            self.gasPriceThread.quit()
            self.gasPriceThread.wait()

        self.close()

    def addMenuLabel(self, layout, text):
        label = QLabel(text)
        layout.addWidget(label)

    def addButton(self, layout, text, function):
        button = QPushButton(text)
        button.clicked.connect(function)
        layout.addWidget(button)

    # execute with html convert
    def executeCommandWithHtmlFormat(self, command, displayWidget, count=1):
        def updateDisplay(output):
            # 追加新的 HTML 输出到日志显示区域
            newHtml = Util.ansiToHtml(output)
            displayWidget.insertHtml(newHtml)
            displayWidget.moveCursor(QTextCursor.End)

        thread = CommandThread(command, count)
        self.commandThreads.append(thread)
        thread.newOutput.connect(updateDisplay)
        thread.start()
        return thread

    # execute with pure text append
    def executeCommand(self, command, displayWidget):
        def updateDisplay(output):
            # 追加新输出到日志显示区域
            displayWidget.append(output)
            displayWidget.moveCursor(QTextCursor.End)

        thread = CommandThread(command)
        self.commandThreads.append(thread)
        thread.newOutput.connect(updateDisplay)
        thread.start()
        return thread

    def createScrollableLogDisplay(self):
        # 创建一个滚动区域
        scrollArea = QScrollArea()
        scrollAreaWidgetContents = QWidget()
        scrollAreaLayout = QVBoxLayout(scrollAreaWidgetContents)

        # 日志输出显示在 QTextEdit 中
        outputDisplay = QTextEdit()
        outputDisplay.setReadOnly(True)  # 设置为只读
        outputDisplay.setWordWrapMode(QTextOption.WordWrap)  # 允许文本换行
        scrollAreaLayout.addWidget(outputDisplay)
        outputDisplay.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)  # 允许文本通过鼠标和键盘被选择和复制

        scrollArea.setWidget(scrollAreaWidgetContents)
        scrollArea.setWidgetResizable(True)  # 允许滚动区域内容自适应大小

        return scrollArea, outputDisplay

    def addTab2(self, content, title):
        tabIndex = self.tabWidget.addTab(content, title)
        self.tabWidget.setCurrentIndex(tabIndex)

    def addTab(self, title, content):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel(content))
        self.tabWidget.addTab(tab, title)

    def closeTab(self, index):
        self.tabWidget.removeTab(index)

    # 命令帮助
    def openCLIhelpTab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        layout.addWidget(scrollArea)

        self.addTab2(tab, "显示命令帮助")

        self.executeCommand("yarn cli --help", outputDisplay)

    # 版本
    def openCLIversionTab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()

        layout.addWidget(scrollArea)
        self.addTab2(tab, "CLI版本")

        self.executeCommandWithHtmlFormat("yarn cli --version", outputDisplay)

    # 服务器版本
    def openServerVersionTab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        layout.addWidget(scrollArea)

        self.addTab2(tab, "服务器版本信息")

        self.executeCommandWithHtmlFormat("yarn cli server-version", outputDisplay)

    # 关于
    def openAboutTab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        layout.addWidget(scrollArea)

        self.addTab2(tab, "关于")

        # 定义一个格式化函数，用于对齐文本
        def format_line(label, content):
            return f"{label}{'   '}{content}"

        # 使用格式化函数来创建对齐的文本
        aboutStr = '\n'.join([
            format_line('脚本作者:', 'wusimpl & redamancyer.eth'),
            format_line('日期:', '2023.12.25'),
            format_line('推特:', '@wusimpl & @quantalmatrix'),
            format_line('支持的 atomicals-js 版本:', 'v0.1.61'),
            format_line('atomicals-js-qt-gui 版本:', 'v2.0'),
            '',
            '注意: 开源脚本，风险自负！'
        ])

        outputDisplay.setText(aboutStr)

    def fetchAndDisplayGasPrice(self, displayWidget,feeRateEdit,logDisplay):
        if self.gasPriceThread is None:
            self.gasPriceThread = GasPriceThread()
        else:
            if self.gasPriceThread.isRunning():
                self.gasPriceThread.quit()
                self.gasPriceThread.wait()

        self.gasPriceThread.setUI(displayWidget,feeRateEdit,logDisplay)
        self.gasPriceThread.start()

    # 查看钱包
    def openDisplayWalletTab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        layout.addWidget(scrollArea)
        self.addTab2(tab, "查看钱包")

        try:
            walletPath = os.environ["WALLET_PATH"]
            if walletPath.startswith("./"):
                walletPath = os.environ["WALLET_PATH"][2:]
            fullWalletFilePath = os.path.join(os.environ["AJS_PATH"], walletPath, os.environ["WALLET_FILE"])
            Util.debugPrint(fullWalletFilePath)
            with open(fullWalletFilePath, "r") as f:
                walletJson = json.load(f)
            outputDisplay.append("=" * 30 + " 主钱包 " + "=" * 30)
            if walletJson["primary"]:
                outputDisplay.append("primary")
                outputDisplay.append(f"address: {walletJson['primary']['address']}")
                outputDisplay.append(f"path: {walletJson['primary']['path']}")
                outputDisplay.append("\n")
            if walletJson["funding"]:
                outputDisplay.append("funding")
                outputDisplay.append(f"address: {walletJson['funding']['address']}")
                outputDisplay.append(f"path: {walletJson['funding']['path']}")
            if walletJson["imported"]:
                outputDisplay.append("\n\n" + "=" * 30 + "导入钱包" + "=" * 30)
                for key in walletJson["imported"]:
                    outputDisplay.append(f"{key}")
                    outputDisplay.append(f"address: {walletJson['imported'][key]['address']}")
                    outputDisplay.append("\n")
        except Exception as e:
            outputDisplay.append(f"读取钱包文件时发生错误: {e}")
            return

    # 钱包初始化
    def openWalletInitTab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()

        layout.addWidget(scrollArea)
        self.addTab2(tab, "初始化主钱包")

        self.executeCommandWithHtmlFormat(f"yarn cli wallet-init", outputDisplay)

    # 导出私钥
    def openExportPrivateKeyTab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        phraseEdit = QLineEdit()
        phraseEdit.setPlaceholderText("请输入助记词短语")
        executeButton = QPushButton("导出私钥")
        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        layout.addWidget(phraseEdit)
        layout.addWidget(executeButton)
        layout.addWidget(scrollArea)
        self.addTab2(tab, "使用助记词导出私钥")

        executeButton.clicked.connect(
            lambda: self.executeCommandWithHtmlFormat(f"yarn cli wallet-decode \"{phraseEdit.text()}\"", outputDisplay))

    # 导入钱包
    def openImportWalletTab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        walletInfoLayout = QHBoxLayout()
        wifEdit = QLineEdit()
        wifEdit.setPlaceholderText("WIF格式的私钥")
        aliasEdit = QLineEdit()
        aliasEdit.setPlaceholderText("给钱包取一个别名")
        executeButton = QPushButton("导入私钥地址")
        walletInfoLayout.addWidget(wifEdit)
        walletInfoLayout.addWidget(aliasEdit)
        walletInfoLayout.addWidget(executeButton)
        walletInfoLayout.setStretchFactor(wifEdit, 2)
        walletInfoLayout.setStretchFactor(aliasEdit, 2)
        walletInfoLayout.setStretchFactor(executeButton, 1)
        layout.addLayout(walletInfoLayout, 0, 0)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        layout.addWidget(scrollArea)

        self.addTab2(tab, "导入私钥地址")

        executeButton.clicked.connect(
            lambda: self.executeCommandWithHtmlFormat(f"yarn cli wallet-import \"{wifEdit.text()}\" \"{aliasEdit.text()}\"",
                                                      outputDisplay))

    # 获取地址信息
    def openAddressInfoTab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        addressEdit = QLineEdit()
        addressEdit.setPlaceholderText("地址")
        executeButton = QPushButton("获取地址信息")
        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        layout.addWidget(addressEdit)
        layout.addWidget(executeButton)
        layout.addWidget(scrollArea)
        self.addTab2(tab, "获取地址信息")

        executeButton.clicked.connect(
            lambda: self.executeCommandWithHtmlFormat(f"yarn cli address \"{addressEdit.text()}\"", outputDisplay))

    # 设置
    def openSettingsTab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        try:
            Util.loadUIEnv()
            Util.loadAJSEnv()
            ajsPath = os.environ["AJS_PATH"]  # .uienv
            rpcURL = os.environ["ELECTRUMX_PROXY_BASE_URL"]  # .env
        except KeyError as e:
            Util.debugPrint(f"error: {e}")
            rpcURL = ""

        ajsPathlayout = QHBoxLayout()
        ajsPathLabel = QLabel("atomicals-js 路径:")
        ajsPathEdit = QLineEdit()
        ajsPathEdit.setText(ajsPath)
        ajsPathBrowseButton = QPushButton("选择")
        ajsPathBrowseButton.clicked.connect(lambda: self.openDirDialog(ajsPathEdit))
        ajsCheckAndInstallButton = QPushButton("检查并安装")
        ajsCheckAndInstallButton.clicked.connect(lambda: self.checkAndInstall(ajsPathEdit, outputDisplay))
        ajsPathlayout.addWidget(ajsPathLabel)
        ajsPathlayout.addWidget(ajsPathEdit)
        ajsPathlayout.addWidget(ajsPathBrowseButton)
        ajsPathlayout.addWidget(ajsCheckAndInstallButton)
        ajsPathlayout.setStretchFactor(ajsPathLabel, 1)
        ajsPathlayout.setStretchFactor(ajsPathEdit, 5)
        ajsPathlayout.setStretchFactor(ajsPathBrowseButton, 1)
        ajsPathlayout.setStretchFactor(ajsCheckAndInstallButton, 1)

        rpcURLLayout = QHBoxLayout()
        rpcURLLabel = QLabel("Atomicals RPC 节点 URL:")
        rpcURLEdit = QLineEdit()
        rpcURLEdit.setText(rpcURL)
        rpcURLTestButton = QPushButton("测试")
        rpcURLTestButton.clicked.connect(lambda: self.testRPCURL(rpcURLEdit, outputDisplay))
        rpcURLLayout.addWidget(rpcURLLabel)
        rpcURLLayout.addWidget(rpcURLEdit)
        rpcURLLayout.addWidget(rpcURLTestButton)
        rpcURLLayout.setStretchFactor(rpcURLLabel, 1)
        rpcURLLayout.setStretchFactor(rpcURLEdit, 5)
        rpcURLLayout.setStretchFactor(rpcURLTestButton, 1)

        saveLayout = QHBoxLayout()
        saveButton = QPushButton("保存")
        saveButton.clicked.connect(lambda: self.saveSettings(ajsPathEdit, rpcURLEdit, outputDisplay))
        saveLayout.addWidget(saveButton)

        scrollAreaLayout = QHBoxLayout()
        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        scrollAreaLayout.addWidget(scrollArea)

        layout.addLayout(ajsPathlayout, 0, 0)
        layout.addLayout(rpcURLLayout, 1, 0)
        layout.addLayout(saveLayout, 2, 0)
        layout.addLayout(scrollAreaLayout, 3, 0)

        self.addTab2(tab, "设置")

    def checkAndInstall(self, ajsPathEdit, outputDisplay):
        class SetupThread(QThread):
            output_signal = pyqtSignal(str)

            def __init__(self, jspath, outputDisplay):
                QThread.__init__(self)
                self.jspath = jspath
                self.outputDisplay = outputDisplay
                self.output_signal.connect(self.outputDisplay.append)

            def run(self):
                try:
                    self.update_output("检查 atomicals-js 环境中...")

                    if not self.check_command(["node", '--version']):
                        self.update_output("Node.js 未安装，请先安装 Node.js。")
                        return

                    if not self.check_command(["yarn", '--version']):
                        self.update_output("安装 yarn 中...")
                        self.execute_command(['npm', 'install', '-g', 'yarn'], "yarn 安装成功。", "安装 yarn 时出错: ")

                    if not self.check_command(["yarn", 'cli', '-V'], self.jspath):
                        self.execute_command(['yarn', 'install'], "atomicals-js 库依赖安装成功。",
                                             "atomicals-js 库依赖安装时出错: ", self.jspath)
                        self.execute_command(['yarn', 'run', 'build'], "atomicals-js 库安装成功。✅ 记得点击保存按钮噢",
                                             "atomicals-js 库编译时出错: ", self.jspath)
                    else:
                        self.update_output("atomicals-js 环境检查通过。✅")
                except Exception as e:
                    self.update_output(f"发生错误: {e}")

            def check_command(self, command_list, cwd=None):
                try:
                    self.update_output("#" * 40)
                    self.update_output(f"执行命令: " + " ".join(command_list))
                    code = self.execute_command(command_list, "", "", cwd)
                    self.update_output("#" * 40)
                    self.update_output("\n")
                    return code
                except Exception:
                    return False

            def execute_command(self, command, success_message, error_message, cwd=None):
                if platform.system() == 'Windows' and not command[0].endswith('.cmd') and command[0] not in ["node", ]:
                    command[0] += '.cmd'

                process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           text=True)
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.update_output(output.strip())

                retcode = process.poll()
                # Util.debugPrint(f"retcode: {retcode}")
                if retcode == 0:
                    self.update_output(success_message)
                    return True
                elif retcode != 0:
                    self.update_output(error_message)
                    return False

            def update_output(self, message):
                self.output_signal.emit(message)

        self.setup_thread = SetupThread(ajsPathEdit.text(), outputDisplay)

        self.setup_thread.start()

    def testRPCURL(self, rpcURLEdit, outputDisplay):
        rpcURL = rpcURLEdit.text()
        self.executeCommandWithHtmlFormat(f"curl {rpcURL}", outputDisplay)

    def saveSettings(self, ajsPathEdit, rpcURLEdit, outputDisplay):
        ajsPath = ajsPathEdit.text()
        rpcURL = rpcURLEdit.text()
        Util.saveEnv(uienvPath, "AJS_PATH", ajsPath)
        os.environ["AJS_PATH"] = ajsPath
        if rpcURL != "":
            ajsEnvPath = os.path.join(ajsPath, ".env")
            Util.saveEnv(ajsEnvPath, "ELECTRUMX_PROXY_BASE_URL", rpcURL)
            os.environ["ELECTRUMX_PROXY_BASE_URL"] = rpcURL
        Util.loadUIEnv()
        Util.loadAJSEnv()
        Util.debugPrint("保存成功!")
        outputDisplay.append("保存成功!")

    def openDirDialog(self, lineEdit):
        selectedDir = QFileDialog.getExistingDirectory()
        if selectedDir == "":
            return
        lineEdit.setText(selectedDir)

    # 获取主钱包详细信息
    def openMainWalletDetailsTab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        layout.addWidget(scrollArea)
        self.addTab2(tab, "主钱包详细信息")

        self.executeCommandWithHtmlFormat("yarn cli wallets", outputDisplay)

    # 获取导入钱包详细信息
    def openImportedWalletDetailsTab(self):
        tab = QWidget()

        walletLayout = QVBoxLayout(tab)
        walletAliasBox = QComboBox()
        walletLayout.addWidget(walletAliasBox)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        walletLayout.addWidget(scrollArea)

        self.addTab2(tab, "导入钱包详细信息")

        walletAliasBox.currentIndexChanged.connect(
            lambda: self.executeCommandWithHtmlFormat(f"yarn cli wallets --alias {walletAliasBox.currentText()}", outputDisplay))
        walletAliasBox.addItems(Util.getImportedWalletList())

    # 获取领域/子领域信息
    def openRealmInfoTab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        realmLayout = QHBoxLayout()
        realmNameEdit = QLineEdit()
        realmNameEdit.setPlaceholderText("领域/子领域名称")
        executeButton = QPushButton("获取领域/子领域信息")
        realmLayout.addWidget(realmNameEdit)
        realmLayout.addWidget(executeButton)
        realmLayout.setStretchFactor(realmNameEdit, 5)
        realmLayout.setStretchFactor(executeButton, 1)
        layout.addLayout(realmLayout, 0, 0)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        layout.addWidget(scrollArea)

        self.addTab2(tab, "领域/子领域信息")

        executeButton.clicked.connect(
            lambda: self.executeCommandWithHtmlFormat(f"yarn cli resolve \"{realmNameEdit.text()}\"", outputDisplay))

    # mint 领域/子领域

    def openMintRealmTab(self,a):
        tab = QWidget()
        gridLayout = QGridLayout(tab)
        self.addTab2(tab, "mint 领域/子领域")

        # 创建领域名称输入区域
        realmLayout = QHBoxLayout()
        realmLabel = QLabel("领域/子领域名称:")
        realmEdit = QLineEdit()
        realmEdit.setPlaceholderText("输入领域/子领域名称")
        checkButton = QPushButton("查重")

        realmLayout.addWidget(realmLabel)
        realmLayout.addWidget(realmEdit)
        realmLayout.addWidget(checkButton)
        realmLayout.setStretch(0, 1)
        realmLayout.setStretch(1, 1)
        realmLayout.setStretch(2, 1)

        # 添加钱包地址输入控件
        senderLabel = QLabel("钱包发送地址:")
        senderEdit = QLineEdit()
        senderEdit.setPlaceholderText("留空默认为funding address")
        senderLayout = QHBoxLayout()
        senderLayout.addWidget(senderLabel)
        senderLayout.addWidget(senderEdit)

        receiverLabel = QLabel("接收地址:")
        receiverEdit = QLineEdit()
        receiverEdit.setPlaceholderText("留空默认为primary address")
        receiverLayout = QHBoxLayout()
        receiverLayout.addWidget(receiverLabel)
        receiverLayout.addWidget(receiverEdit)

        # 添加 satsoutput 和手续费率输入控件
        satsoutputLabel = QLabel("satsoutput:")
        satsoutputEdit = QLineEdit()
        satsoutputEdit.setPlaceholderText("留空则默认1000")
        satsoutputLayout = QHBoxLayout()
        satsoutputLayout.addWidget(satsoutputLabel)
        satsoutputLayout.addWidget(satsoutputEdit)

        feeRateLabel = QLabel("手续费率:")
        feeRateEdit = QLineEdit()
        feeRateEdit.setPlaceholderText("单位：satsbyte，留空默认40")
        feeRateLayout = QHBoxLayout()
        feeRateLayout.addWidget(feeRateLabel)
        feeRateLayout.addWidget(feeRateEdit)

        # 显示当前 gas 价格及刷新按钮
        gasPriceDisplay = QLabel()
        refreshGasButton = QPushButton("刷新")
        refreshGasButton.clicked.connect(lambda: self.fetchAndDisplayGasPrice(gasPriceDisplay,feeRateEdit,outputDisplay))
        gasLayout = QHBoxLayout()
        gasLayout.addWidget(gasPriceDisplay)
        gasLayout.addWidget(refreshGasButton)

        # 执行按钮和输出显示
        executeButton = QPushButton("mint 领域/子领域")
        executeButton.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        gridLayout.addWidget(executeButton, 1, 3, 2, 2)

        # 停止
        stopButton = QPushButton("停止")
        stopButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        gridLayout.addWidget(stopButton, 3, 3, 2, 2)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        self.fetchAndDisplayGasPrice(gasPriceDisplay, feeRateEdit, outputDisplay)

        gridLayout.addLayout(realmLayout, 0, 0, 1, 3)

        gridLayout.addWidget(senderLabel, 1, 0)
        gridLayout.addWidget(senderEdit, 1, 1, 1, 2)

        gridLayout.addWidget(receiverLabel, 2, 0)
        gridLayout.addWidget(receiverEdit, 2, 1, 1, 2)

        gridLayout.addWidget(satsoutputLabel, 3, 0)
        gridLayout.addWidget(satsoutputEdit, 3, 1, 1, 2)

        gridLayout.addWidget(feeRateLabel, 4, 0)
        gridLayout.addWidget(feeRateEdit, 4, 1, 1, 2)

        gridLayout.addWidget(gasPriceDisplay, 5, 0)
        gridLayout.addWidget(refreshGasButton, 5, 1, 1, 2)

        gridLayout.addWidget(scrollArea, 6, 0, 1, 5)

        # 设置执行按钮的点击事件
        executeButton.clicked.connect(lambda: self.mintRealm(
            realmEdit.text(),
            senderEdit.text(),
            receiverEdit.text(),
            satsoutputEdit.text(),
            feeRateEdit.text(),
            outputDisplay,
            stopButton
        ))

        # 设置刷新Gas按钮的点击事件
        refreshGasButton.clicked.connect(lambda: self.fetchAndDisplayGasPrice(gasPriceDisplay,feeRateEdit,outputDisplay))

        # 绑定查重按钮事件
        checkButton.clicked.connect(lambda: self.checkRealmDuplicate(realmEdit.text(), outputDisplay))

    def checkRealmDuplicate(self, realmName, outputDisplay):
        if realmName:
            command = f"yarn cli resolve \"{realmName}\""
            self.executeCommand(command, outputDisplay)
        else:
            outputDisplay.append("领域名称不能为空！")

    def mintRealm(self, realm, sender, receiver, satsoutput, feeRate, displayWidget, stopButton):
        # 检查领域名称是否存在和有效
        # [这里添加检查领域名称的代码]

        # 使用默认值处理可选参数
        sender = f"--funding {sender}" if sender else ""
        receiver = f"--initialowner {receiver}" if receiver else ""
        satsoutput = f"--satsoutput {satsoutput}" if satsoutput else "--satsoutput 1000"
        feeRate = f"--satsbyte {feeRate}" if feeRate else "--satsbyte 40"

        # 构建命令
        mint_realm_cmd = f"yarn cli mint-realm {realm} {feeRate} {sender} {receiver} {satsoutput}"
        # 在单独的线程中执行命令
        thread = self.executeCommandWithHtmlFormat(mint_realm_cmd, displayWidget)
        stopButton.clicked.connect(lambda: self.stopCommandThread(displayWidget, thread))

    # mint NFT
    def openMintNftTab(self):
        tab = QWidget()
        gridLayout = QGridLayout(tab)
        self.addTab2(tab, "mint NFT")

        # 创建文件路径输入区域
        fileLayout = QHBoxLayout()
        fileLabel = QLabel("选择文件路径:")
        filePathEdit = QLineEdit()
        # filePathEdit.setPlaceholderText("文件路径（最好使用全路径）")
        browseButton = QPushButton("浏览")
        browseButton.clicked.connect(lambda: self.openFileDialog(filePathEdit,"*"))
        fileLayout.addWidget(fileLabel)
        fileLayout.addWidget(filePathEdit)
        fileLayout.addWidget(browseButton)
        fileLayout.setStretchFactor(fileLabel, 2)
        fileLayout.setStretchFactor(filePathEdit, 3)
        fileLayout.setStretchFactor(browseButton, 1)

        # 创建其他输入控件
        bitworkcLayout = QHBoxLayout()
        bitworkcLabel = QLabel("bitworkc:")
        bitworkcEdit = QLineEdit()
        bitworkcEdit.setPlaceholderText("bitworkc")
        bitworkcLayout.addWidget(bitworkcLabel)
        bitworkcLayout.addWidget(bitworkcEdit)
        bitworkcLayout.setStretchFactor(bitworkcEdit, 2)
        bitworkcLayout.setStretchFactor(bitworkcLabel, 1)

        satsoutputLayout = QHBoxLayout()
        satsoutputLabel = QLabel("satsoutput:")
        satsoutputEdit = QLineEdit()
        satsoutputEdit.setPlaceholderText("留空则默认1000")
        satsoutputLayout.addWidget(satsoutputLabel)
        satsoutputLayout.addWidget(satsoutputEdit)
        satsoutputLayout.setStretchFactor(satsoutputEdit, 2)
        satsoutputLayout.setStretchFactor(satsoutputLabel, 1)

        senderLayout = QHBoxLayout()
        senderLabel = QLabel("Sender:")
        senderEdit = QLineEdit()
        senderEdit.setPlaceholderText("留空默认为funding address")
        senderLayout.addWidget(senderLabel)
        senderLayout.addWidget(senderEdit)
        senderLayout.setStretchFactor(senderEdit, 2)
        senderLayout.setStretchFactor(senderLabel, 1)

        receiverLayout = QHBoxLayout()
        receiverLabel = QLabel("Receiver:")
        receiverEdit = QLineEdit()
        receiverEdit.setPlaceholderText("留空默认为primary address")
        receiverLayout.addWidget(receiverLabel)
        receiverLayout.addWidget(receiverEdit)
        receiverLayout.setStretchFactor(receiverEdit, 2)
        receiverLayout.setStretchFactor(receiverLabel, 1)

        feeRateLayout = QHBoxLayout()
        feeRateLabel = QLabel("手续费:")
        feeRateEdit = QLineEdit()
        feeRateEdit.setPlaceholderText("留空默认40")
        feeRateLayout.addWidget(feeRateLabel)
        feeRateLayout.addWidget(feeRateEdit)
        feeRateLayout.setStretchFactor(feeRateEdit, 2)
        feeRateLayout.setStretchFactor(feeRateLabel, 1)

        # 显示当前 gas 价格及刷新按钮
        gasLayout = QHBoxLayout()
        gasPriceDisplay = QLabel()
        refreshGasButton = QPushButton("刷新")
        refreshGasButton.clicked.connect(lambda: self.fetchAndDisplayGasPrice(gasPriceDisplay,feeRateEdit,outputDisplay))
        gasLayout.addWidget(gasPriceDisplay)
        gasLayout.addWidget(refreshGasButton)
        gasLayout.setStretchFactor(gasPriceDisplay, 1)
        gasLayout.setStretchFactor(refreshGasButton, 2)

        # 执行按钮和输出显示
        executeButton = QPushButton("mint")
        gridLayout.addWidget(executeButton, 1, 3, 2, 2)
        executeButton.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        stopButton = QPushButton("停止")
        stopButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        gridLayout.addWidget(stopButton, 3, 3, 2, 2)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        self.fetchAndDisplayGasPrice(gasPriceDisplay, feeRateEdit, outputDisplay)

        # 添加控件到布局
        gridLayout.addLayout(fileLayout, 0, 0, 1, 3)
        gridLayout.addLayout(bitworkcLayout, 1, 0, 1, 3)
        gridLayout.addLayout(satsoutputLayout, 2, 0, 1, 3)
        gridLayout.addLayout(senderLayout, 3, 0, 1, 3)
        gridLayout.addLayout(receiverLayout, 4, 0, 1, 3)
        gridLayout.addLayout(feeRateLayout, 5, 0, 1, 3)
        gridLayout.addLayout(gasLayout, 6, 0, 1, 3)

        gridLayout.addWidget(scrollArea, 7, 0, 1, 5)

        # 设置执行按钮的点击事件
        executeButton.clicked.connect(
            lambda: self.mintNFT(filePathEdit.text(), bitworkcEdit.text(), satsoutputEdit.text(),
                                 senderEdit.text(), receiverEdit.text(), feeRateEdit.text(), outputDisplay, stopButton
                                 ))

    def openFileDialog(self, edit,filter):
        fileName, _ = QFileDialog.getOpenFileName(self, "打开文件", "", filter)
        if fileName:
            edit.setText(fileName)

    def mintNFT(self, filePath, bitworkc, satsoutput, sender, receiver, feeRate, displayWidget, stopButton):
        # 检查文件路径是否存在
        if not filePath or not os.path.exists(filePath):
            displayWidget.setText("文件路径不能为空或文件不存在")
            return

        # 使用默认值处理可选参数
        bitworkc = f"--bitworkc {bitworkc}" if bitworkc else ""
        satsoutput = f"--satsoutput {satsoutput}" if satsoutput else "--satsoutput 1000"
        feeRate = f"--satsbyte {feeRate}" if feeRate else "--satsbyte 40"
        sender = f"--funding {sender}" if sender else ""
        receiver = f"--initialowner {receiver}" if receiver else ""

        # 构建命令
        mint_nft_cmd = f"yarn cli mint-nft \"{filePath}\" {bitworkc} {satsoutput} {feeRate} {sender} {receiver}"
        Util.debugPrint(mint_nft_cmd)
        # 在单独的线程中执行命令
        thread = self.executeCommandWithHtmlFormat(mint_nft_cmd, displayWidget)
        stopButton.clicked.connect(lambda: self.stopCommandThread(displayWidget, thread))

    # mint FT
    def openMintDFTTab(self):
        tab = QWidget()
        gridLayout = QGridLayout(tab)
        self.addTab2(tab, "mint FT（ARC20 Token）")

        # Ticker 名称
        tickerLayout = QHBoxLayout()
        tickerLabel = QLabel("Ticker 名称:")
        tickerEdit = QLineEdit()
        tickerEdit.setPlaceholderText("Ticker 名称")
        tickerLayout.addWidget(tickerLabel)
        tickerLayout.addWidget(tickerEdit)
        tickerLayout.setStretchFactor(tickerLabel, 1)
        tickerLayout.setStretchFactor(tickerEdit, 2)

        # 钱包发送地址
        senderLayout = QHBoxLayout()
        senderLabel = QLabel("钱包发送地址:")
        senderEdit = QLineEdit()
        senderEdit.setPlaceholderText("留空则默认为funding address")
        senderLayout.addWidget(senderLabel)
        senderLayout.addWidget(senderEdit)
        senderLayout.setStretchFactor(senderLabel, 1)
        senderLayout.setStretchFactor(senderEdit, 2)

        # 接收地址
        receiverLayout = QHBoxLayout()
        receiverLabel = QLabel("接收地址:")
        receiverEdit = QLineEdit()
        receiverEdit.setPlaceholderText("留空则默认为primary address")
        receiverLayout.addWidget(receiverLabel)
        receiverLayout.addWidget(receiverEdit)
        receiverLayout.setStretchFactor(receiverLabel, 1)
        receiverLayout.setStretchFactor(receiverEdit, 2)

        # 重复mint的数量
        repeatMintLayout = QHBoxLayout()
        repeatMintLabel = QLabel("重复mint数量:")
        repeatMintEdit = QLineEdit()
        repeatMintEdit.setPlaceholderText("留空则默认1张")
        repeatMintLayout.addWidget(repeatMintLabel)
        repeatMintLayout.addWidget(repeatMintEdit)
        repeatMintLayout.setStretchFactor(repeatMintLabel, 1)
        repeatMintLayout.setStretchFactor(repeatMintEdit, 2)

        # 禁用实时挖矿记录
        disableChalkLayout = QHBoxLayout()
        disableChalkLabel = QLabel("禁用实时挖矿记录:")
        disableChalkCheckbox = QCheckBox("禁用")
        disableChalkLayout.addWidget(disableChalkLabel)
        disableChalkLayout.addWidget(disableChalkCheckbox)
        disableChalkLayout.setStretchFactor(disableChalkLabel, 1)
        disableChalkLayout.setStretchFactor(disableChalkCheckbox, 2)

        enableRBFLayout = QHBoxLayout()
        enableRBFLabel = QLabel("启用RBF:")
        enableRBFCheckbox = QCheckBox("启用")
        enableRBFLayout.addWidget(enableRBFLabel)
        enableRBFLayout.addWidget(enableRBFCheckbox)
        enableRBFLayout.setStretchFactor(enableRBFLabel, 1)
        enableRBFLayout.setStretchFactor(enableRBFCheckbox, 2)

        # 手续费率
        feeRateLayout = QHBoxLayout()
        feeRateLabel = QLabel("手续费率:")
        feeRateEdit = QLineEdit()
        feeRateEdit.setPlaceholderText("单位：satsbyte，留空默认40")
        feeRateLayout.addWidget(feeRateLabel)
        feeRateLayout.addWidget(feeRateEdit)
        feeRateLayout.setStretchFactor(feeRateLabel, 1)
        feeRateLayout.setStretchFactor(feeRateEdit, 2)

        # 显示当前 gas 价格
        gasLayout = QHBoxLayout()
        gasPriceDisplay = QLabel()
        refreshGasButton = QPushButton("刷新")
        refreshGasButton.clicked.connect(lambda: self.fetchAndDisplayGasPrice(gasPriceDisplay,feeRateEdit,outputDisplay))
        gasLayout.addWidget(gasPriceDisplay)
        gasLayout.addWidget(refreshGasButton)
        gasLayout.setStretchFactor(gasPriceDisplay, 1)
        gasLayout.setStretchFactor(refreshGasButton, 2)

        # 执行按钮和输出显示
        executeButton = QPushButton("mint FT")
        executeButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        stopButton = QPushButton("停止")
        stopButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        self.fetchAndDisplayGasPrice(gasPriceDisplay, feeRateEdit, outputDisplay)

        # 添加控件到布局
        gridLayout.addLayout(tickerLayout, 0, 0, 1, 3)
        gridLayout.addLayout(senderLayout, 1, 0, 1, 3)
        gridLayout.addLayout(receiverLayout, 2, 0, 1, 3)
        gridLayout.addLayout(repeatMintLayout, 3, 0, 1, 3)
        gridLayout.addLayout(disableChalkLayout, 4, 0, 1, 3)
        gridLayout.addLayout(enableRBFLayout, 5, 0, 1, 3)
        gridLayout.addLayout(feeRateLayout, 6, 0, 1, 3)
        gridLayout.addLayout(gasLayout, 7, 0, 1, 3)
        gridLayout.addWidget(executeButton, 1, 3, 2, 2)
        gridLayout.addWidget(stopButton, 3, 3, 2, 2)
        gridLayout.addWidget(scrollArea, 8, 0, 1, 5)

        # 设置执行按钮的点击事件
        executeButton.clicked.connect(
            lambda: self.mintDFT(tickerEdit.text(), senderEdit.text(), receiverEdit.text(), repeatMintEdit.text(),
                                 disableChalkCheckbox.isChecked(),
                                 enableRBFCheckbox.isChecked(), feeRateEdit.text(), outputDisplay, stopButton))

    def mintDFT(self, ticker, sender, receiver, repeatMint, disableChalk, enbleRBF, feeRate, outputDisplay, stopButton):

        try:
            repeatMint = int(repeatMint)
        except ValueError:
            repeatMint = 1
        # 使用默认值处理可选参数
        feeRate = f"--satsbyte {feeRate}" if feeRate else "--satsbyte 40"
        sender = f"--funding {sender}" if sender else ""
        receiver = f"--initialowner {receiver}" if receiver else ""

        # 构建命令
        mint_dft_cmd = f"yarn cli mint-dft {ticker} {feeRate} {sender} {receiver}"
        if disableChalk:
            mint_dft_cmd = mint_dft_cmd + " --disablechalk"
        if enbleRBF:
            mint_dft_cmd = mint_dft_cmd + " --enable-rbf"

        Util.debugPrint(mint_dft_cmd)
        # 在单独的线程中执行命令
        thread = self.executeCommandWithHtmlFormat(mint_dft_cmd, outputDisplay, repeatMint)
        stopButton.clicked.connect(lambda: self.stopCommandThread(outputDisplay, thread))

    def openMintContainerItemTab(self,a):
        tab = QWidget()
        gridLayout = QGridLayout(tab)
        self.addTab2(tab, "mint Container Item")

        # Container 名称
        containerNameLabel = QLabel("Container 名称:")
        containerNameEdit = QLineEdit()
        containerNameEdit.setPlaceholderText("Container 名称")
        containerCheckButton = QPushButton("查询Container元数据")
        containerNameLayout = QHBoxLayout()
        containerNameLayout.addWidget(containerNameLabel)
        containerNameLayout.addWidget(containerNameEdit)
        containerNameLayout.addWidget(containerCheckButton)
        containerNameLayout.setStretchFactor(containerNameLabel, 1)
        containerNameLayout.setStretchFactor(containerNameEdit, 1)
        containerNameLayout.setStretchFactor(containerCheckButton, 1)
        gridLayout.addLayout(containerNameLayout, 0, 0, 1, 3)

        start_time = time.time()  # 开始计时
        # Item 编号
        itemNameLabel = QLabel("Item 编号:")
        itemNameEdit = QLineEdit()
        checkButton = QPushButton("查重")
        itemNameEdit.setPlaceholderText("Item 编号")
        itemNameLayout = QHBoxLayout()
        itemNameLayout.addWidget(itemNameLabel)
        itemNameLayout.addWidget(itemNameEdit)
        itemNameLayout.addWidget(checkButton)
        itemNameLayout.setStretchFactor(itemNameLabel, 2)
        itemNameLayout.setStretchFactor(itemNameEdit, 3)
        itemNameLayout.setStretchFactor(checkButton, 1)

        gridLayout.addLayout(itemNameLayout, 1, 0, 1, 3)

        # 清单文件路径
        manifestFilePathLabel = QLabel("清单文件路径:")
        manifestFilePathEdit = QLineEdit()
        manifestFilePathEdit.setPlaceholderText("json文件")
        browseButton = QPushButton("浏览")
        browseButton.clicked.connect(lambda: self.openFileDialog(manifestFilePathEdit,"*.json"))
        manifestFilePathLayout = QHBoxLayout()
        manifestFilePathLayout.addWidget(manifestFilePathLabel)
        manifestFilePathLayout.addWidget(manifestFilePathEdit)
        manifestFilePathLayout.addWidget(browseButton)
        manifestFilePathLayout.setStretchFactor(manifestFilePathLabel, 2)
        manifestFilePathLayout.setStretchFactor(manifestFilePathEdit, 3)
        manifestFilePathLayout.setStretchFactor(browseButton, 1)
        gridLayout.addLayout(manifestFilePathLayout, 2, 0, 1, 3)

        # 钱包发送地址
        senderLabel = QLabel("钱包发送地址:")
        senderEdit = QLineEdit()
        senderEdit.setPlaceholderText("留空则默认为funding address")
        senderLayout = QHBoxLayout()
        senderLayout.addWidget(senderLabel)
        senderLayout.addWidget(senderEdit)
        senderLayout.setStretchFactor(senderLabel, 1)
        senderLayout.setStretchFactor(senderEdit, 2)
        gridLayout.addLayout(senderLayout, 3, 0, 1, 3)

        # 接收地址
        receiverLabel = QLabel("接收地址:")
        receiverEdit = QLineEdit()
        receiverEdit.setPlaceholderText("留空则默认为primary address")
        receiverLayout = QHBoxLayout()
        receiverLayout.addWidget(receiverLabel)
        receiverLayout.addWidget(receiverEdit)
        receiverLayout.setStretchFactor(receiverLabel, 1)
        receiverLayout.setStretchFactor(receiverEdit, 2)
        gridLayout.addLayout(receiverLayout, 4, 0, 1, 3)

        # 手续费率
        feeRateLabel = QLabel("手续费率:")
        feeRateEdit = QLineEdit()
        feeRateEdit.setPlaceholderText("单位：sats/byte，留空默认40")
        feeRateLayout = QHBoxLayout()
        feeRateLayout.addWidget(feeRateLabel)
        feeRateLayout.addWidget(feeRateEdit)
        feeRateLayout.setStretchFactor(feeRateLabel, 1)
        feeRateLayout.setStretchFactor(feeRateEdit, 2)
        gridLayout.addLayout(feeRateLayout, 5, 0, 1, 3)

        # 禁用实时挖矿记录
        disableChalkLabel = QLabel("禁用实时挖矿记录:")
        disableChalkCheckbox = QCheckBox("禁用")
        disableChalkLayout = QHBoxLayout()
        disableChalkLayout.addWidget(disableChalkLabel)
        disableChalkLayout.addWidget(disableChalkCheckbox)
        disableChalkLayout.setStretchFactor(disableChalkLabel, 1)
        disableChalkLayout.setStretchFactor(disableChalkCheckbox, 2)
        gridLayout.addLayout(disableChalkLayout, 6, 0, 1, 3)

        # Bitworkc 工作量证明字符串
        bitworkcLabel = QLabel("Bitworkc 工作量证明字符串:")
        bitworkcEdit = QLineEdit()
        bitworkcEdit.setPlaceholderText("留空则默认不使用")
        bitworkcLayout = QHBoxLayout()
        bitworkcLayout.addWidget(bitworkcLabel)
        bitworkcLayout.addWidget(bitworkcEdit)
        bitworkcLayout.setStretchFactor(bitworkcLabel, 1)
        bitworkcLayout.setStretchFactor(bitworkcEdit, 2)
        gridLayout.addLayout(bitworkcLayout, 7, 0, 1, 3)

        # 显示当前 gas 价格
        gasPriceDisplay = QLabel()
        refreshGasButton = QPushButton("刷新")
        refreshGasButton.clicked.connect(lambda: self.fetchAndDisplayGasPrice(gasPriceDisplay,feeRateEdit,outputDisplay))
        gasLayout = QHBoxLayout()
        gasLayout.addWidget(gasPriceDisplay)
        gasLayout.addWidget(refreshGasButton)
        gasLayout.setStretchFactor(gasPriceDisplay, 1)
        gasLayout.setStretchFactor(refreshGasButton, 2)
        gridLayout.addLayout(gasLayout, 8, 0, 1, 3)

        # 执行
        executeButton = QPushButton("mint Container Item")
        gridLayout.addWidget(executeButton, 1, 3, 2, 2)
        executeButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        start_time = time.time()  # 开始计时
        # 停止
        stopButton = QPushButton("停止")
        stopButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        gridLayout.addWidget(stopButton, 3, 3, 2, 2)

        scrollArea, outputDisplay = self.createScrollableLogDisplay()
        gridLayout.addWidget(scrollArea, 9, 0, 1, 5)

        self.fetchAndDisplayGasPrice(gasPriceDisplay, feeRateEdit, outputDisplay)

        executeButton.clicked.connect(lambda: self.mintContainerItem(containerNameEdit.text(), itemNameEdit.text(),
                                                                     manifestFilePathEdit.text(), senderEdit.text(),
                                                                     receiverEdit.text(),
                                                                     feeRateEdit.text(),
                                                                     disableChalkCheckbox.isChecked(),
                                                                     bitworkcEdit.text(),
                                                                     outputDisplay, stopButton))
        checkButton.clicked.connect(
            lambda: self.checkContainerItemDuplicate(containerNameEdit.text(), itemNameEdit.text(), outputDisplay))
        containerCheckButton.clicked.connect(lambda: self.getContainerMetadata(containerNameEdit.text(), outputDisplay))

    def stopCommandThread(self, outputDisplay, thread):
        thread.stop()
        outputDisplay.append("已停止⛔")
        outputDisplay.moveCursor(QTextCursor.End)

    def mintContainerItem(self, containerName, itemName, manifestFilePath, sender, receiver, feeRate, disableChalk,
                          bitworkc, outputDisplay, stopButton):
        if containerName == "" or itemName == "" or manifestFilePath == "":
            outputDisplay.append("请输入容器名称/物品名称/文件路径")
            return
        try:
            bitworkc = f"--bitworkc {bitworkc}" if bitworkc else ""
            # satsoutput = f"--satsoutput {satsoutput}" if satsoutput else "--satsoutput 1000"
            feeRate = f"--satsbyte {feeRate}" if feeRate else "--satsbyte 40"
            sender = f"--funding {sender}" if sender else ""
            receiver = f"--initialowner {receiver}" if receiver else ""

            command = f"yarn cli mint-item \"{containerName}\" \"{itemName}\" \"{manifestFilePath}\" {sender} {receiver} {feeRate} {disableChalk} {bitworkc} "
            outputDisplay.setText("")  # 清空日志
            thread = self.executeCommandWithHtmlFormat(command, outputDisplay)
            stopButton.clicked.connect(lambda: self.stopCommandThread(outputDisplay, thread))
        except Exception as e:
            QMessageBox.critical(None, "错误", f"发生了一个错误：{e}")

    def openContainerItemImagesTab(self):
        folder_path = ''
        current_page = 0
        images = []
        image_labels = []
        text_labels = []  # 新增一个列表来存放文本标签
        cols = 10  # 假设有 10 列
        item_per_page = 200

        def show_image():
            # Util.debugPrint(len(images))
            for i, pic in enumerate(images):
                pixmap = pic["pixmap"]
                filename = pic["filename"]
                # 设置图片
                image_labels[i].setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
                text_labels[i].setText(filename)

        def page_selected(index):
            if folder_path == "":
                return
            # threads must be killed first!
            for thread in self.itemStatusThreads:
                thread.stop()
            self.itemStatusThreads = []

            nonlocal current_page
            current_page = index
            nonlocal images
            images = load_images(folder_path, current_page, item_per_page)
            show_image()

        def search_btn_clicked(index):
            if folder_path == "" or len(self.itemStatusThreads) != 0:
                return
            # threads must be killed first!
            for thread in self.itemStatusThreads:
                thread.stop()

            self.itemStatusThreads = []

            nonlocal current_page
            current_page = index
            nonlocal images

            num_threads = 10  # 或者你想要的线程数
            images_per_thread = len(images) // num_threads
            for i in range(num_threads):
                start_index = i * images_per_thread
                end_index = start_index + images_per_thread
                if i == num_threads - 1:
                    end_index = len(images)  # 确保最后一个线程处理所有剩余的图片

                thread = GetContainerItemStatusThread(images[start_index:end_index], folder_path,
                                                      text_labels[start_index:end_index])
                self.itemStatusThreads.append(thread)
                thread.updateStatusSingal.connect(lambda text_label, text: text_label.setText(text))
                thread.start()

        def select_folder(folder_displayer, page_selector):
            for thread in self.itemStatusThreads:
                thread.stop()

            self.itemStatusThreads = []

            nonlocal folder_path
            folder_path = QFileDialog.getExistingDirectory(tab, "Select Folder")
            nonlocal images
            if folder_path and folder_path != "":
                itemNum = Util.count_files_with_regex(folder_path, "item-(\d+)\.json")
                if itemNum == 0:
                    QMessageBox.warning(None,"警告","文件夹内无符合规范的json文件！")
                    return
                folder_displayer.setText(folder_path)
                # Util.debugPrint(f"itemNum:{itemNum}")
                pageNum = math.ceil(itemNum // item_per_page)
                page_selector.clear()
                for i in range(1, pageNum + 1):
                    page_selector.addItem(f"Page {i}")
                current_page = 0
                page_selector.setCurrentIndex(current_page)
                images = load_images(folder_path, current_page, item_per_page)
                show_image()

        def load_images(folder_path, page, images_per_page):
            images = []  # QPixmap objects
            start = page * images_per_page
            end = start + images_per_page

            def is_valid_file(filename):
                parts = filename.split('-')
                return len(parts) == 2

            file_names = sorted(
                filter(is_valid_file, os.listdir(folder_path)),
                key=lambda x: int(x.split('-')[1].split('.')[0])
            )

            selected_files = file_names[start:end]

            for filename in selected_files:
                if filename.endswith('.json'):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        png_hex_data = data['data']['image.png'].get('$b')
                        png_data = bytes.fromhex(png_hex_data)
                        image = QImage.fromData(png_data)

                        if image.isNull():
                            Util.debugPrint(f"Failed to load image from {file_path}")
                        else:
                            pixmap = QPixmap.fromImage(image)
                            images.append({"pixmap": pixmap, "filename": filename})
            return images

        layout = QVBoxLayout()
        folder_layout = QHBoxLayout()
        tab = QWidget()

        folder_displayer = QLineEdit()
        folder_displayer.setReadOnly(True)
        folder_layout.addWidget(folder_displayer)

        # 创建下拉列表用于选择页码
        page_selector = QComboBox()
        page_selector.currentIndexChanged.connect(page_selected)
        folder_layout.addWidget(page_selector)

        # 添加选择文件夹按钮
        select_folder_button = QPushButton('选择json文件夹')
        select_folder_button.clicked.connect(lambda: select_folder(folder_displayer, page_selector))
        folder_layout.addWidget(select_folder_button)

        search_button = QPushButton('查询mint状态')
        search_button.clicked.connect(lambda: search_btn_clicked(page_selector.currentIndex()))
        folder_layout.addWidget(search_button)

        mintStatusLabel = QLabel()
        mintStatusLabel.setText("已mint：❌   未mint：✅")
        folder_layout.addWidget(mintStatusLabel)

        folder_layout.setStretchFactor(folder_displayer, 4)
        folder_layout.setStretchFactor(select_folder_button, 1)
        folder_layout.setStretchFactor(page_selector, 1)
        folder_layout.setStretchFactor(mintStatusLabel, 1)
        folder_layout.setStretchFactor(search_button, 1)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)

        for i in range(item_per_page):
            # 图片标签
            image_label = QLabel()
            image_labels.append(image_label)
            grid_layout.addWidget(image_label, 2 * (i // cols), i % cols)

            # 文本标签
            text_label = QLabel("")  # 初始文本
            text_label.setAlignment(Qt.AlignCenter)  # 设置文本居中
            text_label.setStyleSheet("color: green; margin: 3px;")
            text_labels.append(text_label)
            grid_layout.addWidget(text_label, 2 * (i // cols) + 1, i % cols)

        scroll_area.setWidget(scroll_widget)

        layout.addLayout(folder_layout)
        layout.addWidget(scroll_area)
        tab.setLayout(layout)

        self.addTab2(tab, "解析 Container Item Images")

    def checkContainerItemDuplicate(self, containerName, itemName, outputDisplay):
        if containerName == "" or itemName == "":
            outputDisplay.append("请输入容器名称/物品名称")
            return
        try:
            command = f"yarn cli get-container-item \"{containerName}\" \"{itemName}\" "
            self.executeCommand(command, outputDisplay)
        except Exception as e:
            QMessageBox.critical(None, "错误", f"发生了一个错误：{e}")

    def getContainerMetadata(self, containerName, outputDisplay):
        if containerName == "":
            outputDisplay.append("请输入容器名称")
            return
        try:
            command = f"yarn cli get-container \"{containerName}\" "
            self.executeCommand(command, outputDisplay)
        except Exception as e:
            QMessageBox.critical(None, "错误", f"发生了一个错误：{e}")


def main():
    signal.signal(signal.SIGINT, signal_handler)

    app = QApplication(sys.argv)
    ex = AtomicalToolGUI()
    ex.show()

    # 使用定时器让Python有机会处理信号
    timer = QTimer()
    timer.start(500)  # 500毫秒
    timer.timeout.connect(lambda: None)  # 仅为了触发Python的信号处理

    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        QMessageBox.critical(None, "错误", f"发生了一个错误：{e}")
