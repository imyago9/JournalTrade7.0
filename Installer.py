import subprocess
import sys
import os
import shutil
from PyQt5 import QtGui
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QRect
from appdirs import AppDirs
import requests

APP_NAME = 'JournalTrade'
APP_AUTHOR = '.JTbyY'

dirs = AppDirs(APP_NAME, APP_AUTHOR)
user_data_dir = dirs.user_data_dir

GITHUB_VERSION_URL = 'https://raw.githubusercontent.com/imyago9/JournalTrade7.0/master/version.txt'
JOURNALTRADE_EXE_URL = 'https://raw.githubusercontent.com/imyago9/JournalTrade7.0/master/dist/JournalTrade.exe'
INSTALLER_EXE_URL = 'https://raw.githubusercontent.com/imyago9/JournalTrade7.0/master/dist/Installer.exe'
LOCAL_VERSION_PATH = os.path.join(user_data_dir, 'version.txt')
LOCAL_EXE_PATH = os.path.join(user_data_dir, 'JournalTrade.exe')
NEW_EXE_PATH = os.path.join(user_data_dir, 'JournalTrade_new.exe')
UPDATER_EXE_PATH = os.path.join(user_data_dir, 'Updater.exe')


def install_application():
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
        print(user_data_dir)


def get_github_version():
    try:
        response = requests.get(GITHUB_VERSION_URL)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching version from GitHub: {e}")
        return None

def get_local_version():
    try:
        with open(LOCAL_VERSION_PATH, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Local version file not found at {LOCAL_VERSION_PATH}")
        return None

def download_file(url, dest_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Downloaded {url} to {dest_path}")
    except requests.RequestException as e:
        print(f"Error downloading file from {url}: {e}")

def download_text_file(url, dest_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(dest_path, 'w') as f:
            f.write(response.text.strip())
        print(f"Downloaded {url} to {dest_path}")
    except requests.RequestException as e:
        print(f"Error downloading file from {url}: {e}")
        raise

def update_application():
    download_file(JOURNALTRADE_EXE_URL, NEW_EXE_PATH)

    if not os.path.exists(UPDATER_EXE_PATH):
        download_file(INSTALLER_EXE_URL, UPDATER_EXE_PATH)

    download_text_file(GITHUB_VERSION_URL, LOCAL_VERSION_PATH)

    subprocess.Popen([UPDATER_EXE_PATH])
    sys.exit()

def check_for_updates():
    github_version = get_github_version(GITHUB_VERSION_URL)
    local_version = get_local_version(os.path.join(os.getenv('LOCALAPPDATA'), 'Y', 'JournalTrade', 'version.txt'))

    if github_version and local_version and github_version != local_version:
        reply = QMessageBox.question(None, 'Update Available',
                                     'A new version of JournalTrade is available. Do you want to update?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            update_application()
        else:
            sys.exit()
    elif local_version is None:
        update_application()
    elif github_version == local_version:
        print(f'Version Match! GitHub Version: {github_version}. Local Version: {local_version}')
        reply = QMessageBox.question(None, 'Open Application?',
                                     'Do you wish to open the application?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            subprocess.Popen([LOCAL_EXE_PATH])
        else:
            print('Nothing happens.')


class InstallerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.saved_loc_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Application Installer')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
        QMainWindow {
            background-color: #222222;
            border: 5px solid #c3dc9b;
            border-radius: 9px;
            color: white;
            margin: -3px;
        }
        
        /* Style for push buttons */
        QPushButton {
            color: white;
            border: 2px solid #c3dc9b;
            border-radius: 9px;
            padding: 1px 2px;
            margin: 2px;
        }
        
        QPushButton:hover {
            background-color: #2c7e33;
        }
        
        /* Style for table headers */
        QHeaderView::section {
            color: #fff;
            font-weight: bold;
            border-top: 0px;
            border-bottom: 0px;
            background-color: #777;
        }""")
        self.setMouseTracking(True)
        screen = QDesktopWidget().screenGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.setGeometry(100, 100, int(self.screen_width * 0.15), int(self.screen_height * 0.3))
        self.top_bar_height = self.screen_height * 0.1

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        button_layout = self.setup_button_layout()
        layout = QVBoxLayout(self.central_widget)
        layout.addLayout(button_layout)
        self.text_label = QLabel('JournalTrade by:')
        self.text_label.setStyleSheet("color: white;")
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QtGui.QPixmap(resource_path("resources/kyro_logo.png")))
        layout.addWidget(self.text_label, alignment=Qt.AlignLeft)
        layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
        options_layout = self.setup_options_layout()
        layout.addLayout(options_layout)

        self.resize_margin = button_layout.geometry().height()

        self.center_window()

    def setup_button_layout(self):
        button_layout = QHBoxLayout()
        close_button = QPushButton('', clicked=self.close)
        minimize_button = QPushButton('', clicked=self.showMinimized)
        button_layout.addWidget(minimize_button)
        button_layout.addWidget(close_button)
        close_button_icon = QtGui.QIcon()
        close_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/close_icon.png")),
                                    QtGui.QIcon.Normal,
                                    QtGui.QIcon.Off)
        minimize_button_icon = QtGui.QIcon()
        minimize_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/minimize_icon.png")),
                                       QtGui.QIcon.Normal,
                                       QtGui.QIcon.Off)

        close_button.setIcon(close_button_icon)
        minimize_button.setIcon(minimize_button_icon)
        return button_layout

    def setup_options_layout(self):
        local_version = get_local_version()
        layout = QVBoxLayout()
        if local_version is None:
            self.install_button = QPushButton('Install JournalTrade', clicked=update_application)
            layout.addWidget(self.install_button)
        else:
            self.update_button = QPushButton('Update JournalTrade', clicked=check_for_updates)
            self.uninstall_button = QPushButton('Uninstall JournalTrade')
            layout.addWidget(self.update_button)
            layout.addWidget(self.uninstall_button)
        return layout

    def mousePressEvent(self, event: QMouseEvent):
        try:
            if event.button() == Qt.LeftButton:
                self.mouse_pos = event.globalPos()
                self.frame_pos = self.frameGeometry().topLeft()
                self.rect_before_resize = self.frameGeometry()
                if event.y() <= self.top_bar_height:
                    self.moving = True
                    self.resizing = None
                else:
                    self.moving = False
                    self.resizing = self.get_resize_direction(event.pos())
        except Exception as e:
            print(f'Error in mousePressEvent: {e}')

    def mouseMoveEvent(self, event: QMouseEvent):
        try:
            if self.moving:
                delta = event.globalPos() - self.mouse_pos
                self.move(self.frame_pos + delta)
            elif self.resizing:
                self.resize_window(event.globalPos())
        except Exception as e:
            print(f'Error in mouseMoveEvent: {e}')

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.moving = False
        self.resizing = None

    def get_resize_direction(self, pos):
        rect = self.rect()
        if pos.x() <= self.resize_margin:
            if pos.y() <= self.resize_margin:
                return 'top_left'
            elif pos.y() >= rect.height() - self.resize_margin:
                return 'bottom_left'
            else:
                return 'left'
        elif pos.x() >= rect.width() - self.resize_margin:
            if pos.y() <= self.resize_margin:
                return 'top_right'
            elif pos.y() >= rect.height() - self.resize_margin:
                return 'bottom_right'
            else:
                return 'right'
        elif pos.y() <= self.resize_margin:
            return 'top'
        elif pos.y() >= rect.height() - self.resize_margin:
            return 'bottom'
        return None

    def resize_window(self, global_pos):
        delta = global_pos - self.mouse_pos
        rect = self.rect_before_resize

        if self.resizing == 'left':
            new_rect = QRect(rect.left() + delta.x(), rect.top(), rect.width() - delta.x(), rect.height())
        elif self.resizing == 'right':
            new_rect = QRect(rect.left(), rect.top(), rect.width() + delta.x(), rect.height())
        elif self.resizing == 'top':
            new_rect = QRect(rect.left(), rect.top() + delta.y(), rect.width(), rect.height() - delta.y())
        elif self.resizing == 'bottom':
            new_rect = QRect(rect.left(), rect.top(), rect.width(), rect.height() + delta.y())
        elif self.resizing == 'top_left':
            new_rect = QRect(rect.left() + delta.x(), rect.top() + delta.y(), rect.width() - delta.x(), rect.height() - delta.y())
        elif self.resizing == 'top_right':
            new_rect = QRect(rect.left(), rect.top() + delta.y(), rect.width() + delta.x(), rect.height() - delta.y())
        elif self.resizing == 'bottom_left':
            new_rect = QRect(rect.left() + delta.x(), rect.top(), rect.width() - delta.x(), rect.height() + delta.y())
        elif self.resizing == 'bottom_right':
            new_rect = QRect(rect.left(), rect.top(), rect.width() + delta.x(), rect.height() + delta.y())

        if new_rect.width() >= self.minimumWidth() and new_rect.height() >= self.minimumHeight():
            self.setGeometry(new_rect)

    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InstallerWindow()
    window.show()
    sys.exit(app.exec_())
