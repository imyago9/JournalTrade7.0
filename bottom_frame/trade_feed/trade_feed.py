import os
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class RecentTradeFeed(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_top_frame()
        self.setLayout(self.main_layout)

    def setup_top_frame(self):
        self.top_frame = QFrame()
        self.top_frame_layout = QHBoxLayout(self.top_frame)
        self.top_frame_layout.setSpacing(0)
        self.top_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.setupTopFrameTitle()
        self.top_frame_layout.addWidget(self.top_frame_title)
        self.top_frame_layout.setStretch(0, 1)
        self.top_frame_layout.setStretch(1, 1)
        self.main_layout.addWidget(self.top_frame)

    def setupTopFrameTitle(self):
        self.top_frame_title = QLabel("Recent Trade Feed")
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.top_frame_title.setFont(font)
        self.top_frame_title.setAlignment(Qt.AlignCenter)

    def start_data_fetching(self):
        # Code to start fetching data
        print("Starting data fetching for RecentTradeFeed")

    def stop_data_fetching(self):
        # Code to stop fetching data
        print("Stopping data fetching for RecentTradeFeed")

    def showEvent(self, event):
        super().showEvent(event)
        self.start_data_fetching()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.stop_data_fetching()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)