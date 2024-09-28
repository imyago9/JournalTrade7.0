from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from SQL import get_screenshot
import os
from bottom_frame.custom_widgets import ClickableLabel


class ImageDropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.line_edit = QLineEdit()
        self.clear_button = QPushButton('-')
        self.clear_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")
        self.line_edit.setAlignment(Qt.AlignCenter)
        self.line_edit.setText("Drop an image here")
        self.line_edit.setStyleSheet('''
            QLineEdit {
                border: 2px dashed #aaa;
                color: #555;
            }
        ''')
        self.line_edit.setReadOnly(True)

        self.clear_button.setEnabled(False)
        self.clear_button.clicked.connect(self.clear_selection)

        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.clear_button)
        self.setLayout(self.layout)
        self.file_path = None

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            file_name = file_path.split('/')[-1]
            name_without_extension = ".".join(file_name.split(".")[:-1])
            self.line_edit.setText(name_without_extension)
            self.clear_button.setEnabled(True)
            self.file_path = file_path
            event.acceptProposedAction()
        else:
            event.ignore()

    def clear_selection(self):
        name = self.get_file_path()
        print(f'File path: {name}')
        self.line_edit.setText("Drop an image here")
        self.clear_button.setEnabled(False)

    def get_file_path(self):
        if self.file_path:
            return self.file_path
        else:
            print('No file path.')

class InteractiveDropArea(QFrame):
    screenshot_clicked = pyqtSignal(QWidget)
    def __init__(self, parent=None, trade_id=None, screenshot_index=None):
        super().__init__(parent)
        self.screenshot = get_screenshot(trade_id, screenshot_index)
        self.screenshot_popup = None
        self.clickable = True

        self.layout = QHBoxLayout()
        self.image_label = ClickableLabel(self, type='ti_ss')
        self.clear_button = QPushButton('-')
        self.clear_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")
        self.clear_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet('''
            QLineEdit {
                border: 2px dashed #aaa;
                color: #555;
            }
        ''')

        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.clear_button)
        self.setLayout(self.layout)
        self.file_path = None

        self.image_label.setText('Drop an image here')
        self.clear_button.setEnabled(False)

        if self.screenshot:
            self.set_screenshot(self.screenshot)

        self.clear_button.clicked.connect(self.clear_selection)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                raise ValueError("Failed to load QPixmap from the dropped file.")
            self.image_label.setPixmap(pixmap)
            self.adjust_pixmap_to_label()
            self.clear_button.setEnabled(True)
            self.file_path = file_path
            if isinstance(file_path, (str, os.PathLike)):
                with open(file_path, 'rb') as file:
                    current_screenshot_data = file.read()
            self.screenshot = current_screenshot_data
            event.acceptProposedAction()
        else:
            event.ignore()

    def resizeEvent(self, event):
        if self.image_label.pixmap():
            self.adjust_pixmap_to_label()
        super().resizeEvent(event)

    def adjust_pixmap_to_label(self):
        pixmap = self.image_label.pixmap()
        if pixmap:
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def set_screenshot(self, screenshot_data):
        if screenshot_data:
            pixmap = QPixmap()
            pixmap.loadFromData(screenshot_data)
            self.image_label.setPixmap(pixmap)
            self.adjust_pixmap_to_label()
            self.clear_button.setEnabled(True)
            self.screenshot = screenshot_data

    def clear_selection(self):
        self.image_label.clear()
        self.clear_button.setEnabled(False)
        self.image_label.setText('Drop an image here')
        self.file_path = None
        self.screenshot = None

    def get_file_path(self):
        return self.file_path if self.file_path else 'No file path.'

    def set_screenshot_first_stack(self):
        try:
            if self.clickable and self.screenshot:
                self.screenshot_popup = ScreenshotPopup(screenshot=self.screenshot)
                self.screenshot_clicked.emit(self.screenshot_popup)
        except Exception as e:
            print(f'Failed to toggle screenshot popup: {e}')

class ScreenshotPopup(QWidget):
    try:
        def __init__(self, parent=None, screenshot=None):
            super().__init__(parent)
            self.screenshot = screenshot

            self.setupUI()

        def setupUI(self):
            frame = QFrame()
            layout = QVBoxLayout(frame)
            self.screenshot_label = QLabel()
            self.update_screenshot(self.screenshot)
            layout.addWidget(self.screenshot_label)
            self.setLayout(layout)

        def update_screenshot(self, screenshot_data):
            if screenshot_data:
                pixmap = QPixmap()
                pixmap.loadFromData(screenshot_data)
                self.screenshot_label.setPixmap(pixmap)
                self.screenshot = screenshot_data

        def set_pixmap_width(self, width):
            if self.screenshot:
                pixmap = QPixmap()
                pixmap.loadFromData(self.screenshot)
                scaled_pixmap = pixmap.scaledToWidth(width, Qt.SmoothTransformation)
                self.screenshot_label.setPixmap(scaled_pixmap)
    except Exception as e:
        print(f'Error loading screenshot popup: {e}')
