import sys
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
import socket
import os
import threading


# os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
class ApplicationThread(QtCore.QThread):
    def __init__(self, application, port):
        super(ApplicationThread, self).__init__()
        self.application = application
        self.port = port

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=self.port, threaded=True)


class WebPage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(QtCore.QUrl(self.root_url))


def launch_gui(application, port=0, window_title="OCR Labeling Tool", icon="./icon.png", argv=None):
    if argv is None:
        argv = sys.argv

    if port == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        sock.close()

    # Application Level
    qtapp = QtWidgets.QApplication(argv)
    # qtapp.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)

    # Main Window Level
    window = QtWidgets.QMainWindow()
    # window.setMinimumSize(1280, 720)
    # Fixed Window Size  
    window.setFixedSize(900, 280)
    # Maximize on launch
    # window.showMaximized()
    # Resize window
    # window.resize(width, height)
    window.setWindowTitle(window_title)
    window.setWindowIcon(QtGui.QIcon(icon))

    # WebView Level
    webView = QtWebEngineWidgets.QWebEngineView(window)
    webView.page().profile().clearHttpCache()
    window.setCentralWidget(webView)

    # WebPage Level
    page = WebPage('http://localhost:{}'.format(port))
    page.home()
    webView.setPage(page)
    window.show()
    return qtapp.exec_()
