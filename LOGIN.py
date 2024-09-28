import sys
import os
import psycopg2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtGui
from SQL import verify_credentials, register_user
from MainWindow import MainWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Login Window')
        self.setWindowFlags(Qt.FramelessWindowHint)
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        self.setGeometry(100, 100, int(screen_width * 0.15), int(screen_height * 0.3))
        self.initializeGUI()
        self._is_dragging = False
        self._drag_start_position = QPoint()
        self.center_window()
        self.username_input.setFocus()
        self.setStyleSheet("""
        QWidget {
            background-color: #222222;
            color: white;
        }""")

    def initializeGUI(self):
        self.main_frame_vertical_layout = QVBoxLayout()
        
        # CREATING TOP FRAME FOR KYRO LOGO
        self.top_frame = QFrame()
        self.top_frame_layout = QVBoxLayout(self.top_frame)

        self.top_frame_button_frame = QFrame()
        self.top_frame_button_layout = QHBoxLayout()
        self.close_button = QPushButton(clicked=self.close)
        self.minimize_button = QPushButton(clicked=self.showMinimized)

        close_button_icon = QtGui.QIcon()
        close_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/close_icon.png")))
        self.close_button.setIcon(close_button_icon)
        minimize_button_icon = QtGui.QIcon()
        minimize_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/minimize_icon.png")))
        self.minimize_button.setIcon(minimize_button_icon)

        self.top_frame_button_layout.addWidget(QLabel('JournalTrades by:'))
        self.top_frame_button_layout.addStretch()
        self.top_frame_button_layout.addWidget(self.minimize_button)
        self.top_frame_button_layout.addWidget(self.close_button)
        self.top_frame_button_frame.setLayout(self.top_frame_button_layout)

        self.top_frame_logo_frame = QFrame()
        self.top_frame_logo_layout = QHBoxLayout()

        self.logo_label = QLabel()
        logo_pixmap = QtGui.QPixmap(resource_path("resources/kyro_logo.png"))
        self.logo_label.setPixmap(logo_pixmap)

        self.top_frame_logo_layout.addWidget(self.logo_label,0, Qt.AlignCenter)
        self.top_frame_logo_frame.setLayout(self.top_frame_logo_layout)

        self.top_frame_layout.addWidget(self.top_frame_button_frame)
        self.top_frame_layout.addWidget(self.top_frame_logo_frame)

        # CREATING BOTTOM FRAME FOR LOGIN/REGISTER
        self.bottom_frame = QFrame()
        self.bottom_frame_layout = QVBoxLayout(self.bottom_frame)

        self.username_label = QLabel('Username')
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("border: 2px solid #c3dc9b;")
        self.password_label = QLabel('Password')
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet("border: 2px solid #c3dc9b;")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_label = QLabel('Confirm Password')
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setStyleSheet("border: 2px solid #c3dc9b;")

        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_label.setVisible(False)
        self.confirm_password_input.setVisible(False)
        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.check_login)
        self.username_input.returnPressed.connect(self.submit_button.click) 
        self.password_input.returnPressed.connect(self.submit_button.click)
        self.register_button = QPushButton('Register')
        self.register_button.clicked.connect(self.show_register_fields)

        self.bottom_frame_layout.addWidget(self.username_label)
        self.bottom_frame_layout.addWidget(self.username_input)
        self.bottom_frame_layout.addWidget(self.password_label)
        self.bottom_frame_layout.addWidget(self.password_input)
        self.bottom_frame_layout.addWidget(self.confirm_password_label)
        self.bottom_frame_layout.addWidget(self.confirm_password_input)
        self.bottom_frame_layout.addWidget(self.submit_button)
        self.bottom_frame_layout.addWidget(self.register_button)

        self.main_frame_vertical_layout.addWidget(self.top_frame)
        self.main_frame_vertical_layout.addWidget(self.bottom_frame)
        self.setLayout(self.main_frame_vertical_layout)


    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if verify_credentials(username, password):
            self.open_main_window()
        else:
            QMessageBox.warning(self, 'Login', 'Login failed')

    def open_main_window(self):
        self.main_window = MainWindow()  # Create an instance of MainWindow
        self.main_window.show()
        self.close()

    def show_register_fields(self):
        self.confirm_password_label.setVisible(True)
        self.confirm_password_input.setVisible(True)
        self.submit_button.setText('Create Account')
        self.submit_button.clicked.disconnect()
        self.submit_button.clicked.connect(self.create_account)
        self.register_button.setText('Back to Login')
        self.register_button.clicked.disconnect()
        self.register_button.clicked.connect(self.show_login_fields)

    def show_login_fields(self):
        self.confirm_password_label.setVisible(False)
        self.confirm_password_input.setVisible(False)
        self.submit_button.setText('Submit')
        self.submit_button.clicked.disconnect()
        self.submit_button.clicked.connect(self.check_login)
        self.register_button.setText('Register')
        self.register_button.clicked.disconnect()
        self.register_button.clicked.connect(self.show_register_fields)

    def create_account(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Username and password cannot be blank.')
            return

        if password != confirm_password:
            QMessageBox.warning(self, 'Error', 'Passwords do not match')
            return
        user_id = register_user(username, password)
        if user_id:
            QMessageBox.information(self, 'Success', 'Account created successfully')
            print(user_id)
            self.show_login_fields()
        else:
            QMessageBox.warning(self, 'Error', 'Username already exists.')


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            self.move(event.globalPos() - self._drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()

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


def load_stylesheet(app):
    stylesheet_path = resource_path('resources/style.qss')
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, "r") as file:
            app.setStyleSheet(file.read())
    else:
        print(f"Error: Stylesheet file not found at path {stylesheet_path}")


def main():
    app = QApplication(sys.argv)
    load_stylesheet(app)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
