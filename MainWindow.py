import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import *

from SQL import *
from bottom_frame.friends_list.friends_list import FriendsList
from bottom_frame.personal_view.personal_account_view import PersonalAccountsView
from bottom_frame.trade_feed.trade_feed import RecentTradeFeed
from bottom_frame.accounts_popup import AccountsPopup


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JournalTrade')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        screen = QDesktopWidget().screenGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        self.setGeometry(100, 100, int(self.screen_width * 0.8), int(self.screen_height * 0.6))

        self.resize_margin = 20
        self.top_bar_height = self.screen_height * 0.1

        self.isTradeFeed = False
        self.accounts_popup = None

        self.setupMainWindow()
        self.center_window()

    def setupMainWindow(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget_layout = QVBoxLayout(self.central_widget)
        self.central_widget_layout.setSpacing(0)

        self.setup_top_frame()
        self.setup_bottom_frame()

        self.central_widget_layout.addWidget(self.top_frame)
        self.central_widget_layout.addWidget(self.bottom_frame)
        self.central_widget_layout.setStretch(0, 0)
        self.central_widget_layout.setStretch(1, 1)

    def setup_top_frame(self):
        try:
            self.top_frame = QFrame()
            self.top_frame_layout = QHBoxLayout(self.top_frame)
            self.top_frame_layout.setSpacing(0)
            self.top_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            self.setup_top_frame_buttons()

            self.top_frame_layout.addWidget(self.friends_view_button)
            self.top_frame_layout.addWidget(self.swtich_view_button)
            self.top_frame_layout.addWidget(self.accounts_list_button)
            self.top_frame_layout.addStretch()
            self.top_frame_layout.addWidget(self.minimize_button)
            self.top_frame_layout.addWidget(self.expand_shrink_button)
            self.top_frame_layout.addWidget(self.close_app_button)
        except Exception as e:
            print(f'Error setting up top frame: {e}')

    def setup_top_frame_buttons(self):
        try:
            self.friends_view_button = QPushButton('', clicked=self.toggle_friends_side_menu)
            self.accounts_list_button = QPushButton('', clicked=self.toggle_accounts_popup)
            self.swtich_view_button = QPushButton('', clicked=self.switch_bottom_right_view)
            self.minimize_button = QPushButton('',clicked=self.showMinimized)
            self.expand_shrink_button = QPushButton('', clicked=self.toggle_window_size)
            self.close_app_button = QPushButton('', clicked=self.close)


            close_button_icon = QtGui.QIcon()
            close_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/close_icon.png")), QtGui.QIcon.Normal,
                                        QtGui.QIcon.Off)
            minimize_button_icon = QtGui.QIcon()
            minimize_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/minimize_icon.png")),
                                           QtGui.QIcon.Normal,
                                           QtGui.QIcon.Off)
            self.expand_button_icon = QtGui.QIcon()
            self.expand_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/expand_icon.png")), QtGui.QIcon.Normal,
                                         QtGui.QIcon.Off)
            self.shrink_button_icon = QtGui.QIcon()
            self.shrink_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/expand_icon.png")), QtGui.QIcon.Normal,
                                     QtGui.QIcon.Off)
            account_list_button_icon = QtGui.QIcon()
            account_list_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/account_list.png")),
                                           QtGui.QIcon.Normal,
                                           QtGui.QIcon.Off)
            switch_views_button_icon = QtGui.QIcon()
            switch_views_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/switch_views.png")),
                                           QtGui.QIcon.Normal,
                                           QtGui.QIcon.Off)
            friends_button_icon = QtGui.QIcon()
            friends_button_icon.addPixmap(QtGui.QPixmap(resource_path("resources/friends_icon.png")),
                                          QtGui.QIcon.Normal,
                                          QtGui.QIcon.Off)

            self.close_app_button.setIcon(close_button_icon)
            self.expand_shrink_button.setIcon(self.expand_button_icon)
            self.minimize_button.setIcon(minimize_button_icon)
            self.swtich_view_button.setIcon(switch_views_button_icon)
            self.accounts_list_button.setIcon(account_list_button_icon)
            self.friends_view_button.setIcon(friends_button_icon)
        except Exception as e:
            print(f'Error setting up top frame buttons: {e}')

    def toggle_window_size(self):
        if self.isFullScreen():
            self.showNormal()
            self.expand_shrink_button.setIcon(self.expand_button_icon)
        else:
            self.showFullScreen()
            self.expand_shrink_button.setIcon(self.shrink_button_icon)

    def setup_bottom_frame(self):
        try:
            self.bottom_frame = QFrame()
            self.bottom_frame_layout = QHBoxLayout(self.bottom_frame)
            self.bottom_frame_layout.setSpacing(0)
            self.bottom_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.setup_friends_list_side_menu()
            self.stack = QStackedWidget(self.bottom_frame)
            self.bottom_frame_layout.addWidget(self.stack)
            self.bottom_frame_layout.setStretch(0, 0)
            self.bottom_frame_layout.setStretch(1, 1)
            self.setup_bottom_frame_main()
        except Exception as e:
            print(f'Error setting up bottom frame: {e}')

    def setup_friends_list_side_menu(self):
        try:
            self.isMenuVisible = False
            self.friends_list_side_menu = FriendsList(self.bottom_frame)
            self.friends_list_side_menu.setMaximumWidth(0)
            self.friends_list_side_menu.setMinimumWidth(0)
            self.friends_list_side_menu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.bottom_frame_layout.addWidget(self.friends_list_side_menu)
            self.animation = QPropertyAnimation(self.friends_list_side_menu, b"maximumWidth")
        except Exception as e:
            print(f'Error setting up friends side menu: {e}')

    def toggle_friends_side_menu(self):
        try:
            self.animation.stop()
            bottom_frame_width = self.bottom_frame.width()
            self.side_menu_width = int(bottom_frame_width * 0.15)
            if self.isMenuVisible:
                start_width = self.side_menu_width
                end_width = 0
            else:
                start_width = 0
                end_width = self.side_menu_width
                self.update_friends_list()

            self.animation.setDuration(500)
            self.animation.setStartValue(start_width)
            self.animation.setEndValue(end_width)
            self.friends_list_side_menu.setMaximumWidth(self.side_menu_width)
            self.animation.start()
            self.isMenuVisible = not self.isMenuVisible
        except Exception as e:
            print(f'Error toggling friends side menu: {e}')

    def update_friends_list(self):
        try:
            self.friends_list_side_menu.update_friends_list()
        except Exception as e:
            print(f"Error updating friends list: {e}")

    def setup_bottom_frame_main(self):
        try:
            self.personal_view = PersonalAccountsView(parent=None)
            self.trade_feed_view = RecentTradeFeed(parent=None)
            self.stack.addWidget(self.personal_view)
            self.stack.addWidget(self.trade_feed_view)
            self.stack.setCurrentWidget(self.personal_view)
        except Exception as e:
            print(f'Error setting up bottom frame main: {e}')

    def toggle_accounts_popup(self):
        try:
            if self.accounts_popup is None or not self.accounts_popup.isVisible():
                height = int(self.top_frame.height())
                width = int(self.top_frame.width() // 2)
                if self.accounts_popup is None:
                    self.accounts_popup = AccountsPopup(self, width=width, height=height)
                    self.accounts_popup.account_changed.connect(self.account_selected)

                self.animate_accounts_popup(show=True)
                self.personal_view.animate_new_trade_popup(show=False)
                self.move_accounts_popup()
            else:
                self.animate_accounts_popup(show=False)
        except Exception as e:
            print(f'Failed to toggle my accounts list: {e}')


    def account_selected(self, account_id, account_name, account_type):
        try:
            current_title = self.personal_view.top_frame_title.text()
            new_title = f"{account_name}"
            if current_title != new_title:
                self.personal_view.animate_new_trade_popup(show=False)
                self.stack.setCurrentWidget(self.personal_view)
                self.personal_view.current_account = account_name
                self.personal_view.account_id = account_id
                self.personal_view.account_type = account_type
                self.personal_view.new_trade_popup = None
                self.personal_view.top_frame_title.setText(new_title)
                self.personal_view.disable_account_list_signal.connect(self.new_trade_toggles_accounts_popup_off)
                self.personal_view.fetch_account_data(account_id)
                self.animate_accounts_popup(show=False)
                self.center_window()
            else:
                print(f"Account {account_name} is already selected.")
        except Exception as e:
            print(f'Failed to update account data: {e}')

    def new_trade_toggles_accounts_popup_off(self):
        self.animate_accounts_popup(show=False)


    def animate_accounts_popup(self, show=True):
        try:
            if show:
                self.accounts_popup.setWindowOpacity(0)
                self.accounts_popup.show()
                self.account_animation = QPropertyAnimation(self.accounts_popup, b"windowOpacity")
                self.account_animation.setDuration(500)
                self.account_animation.setStartValue(0)
                self.account_animation.setEndValue(1)
            else:
                self.account_animation = QPropertyAnimation(self.accounts_popup, b"windowOpacity")
                self.account_animation.setDuration(500)
                self.account_animation.setStartValue(1)
                self.account_animation.setEndValue(0)
                self.account_animation.finished.connect(self.accounts_popup.hide)
                self.accounts_popup.account_options_view()
            self.account_animation.start()
        except Exception as e:
            print(f'Failed to animate accounts pop up: {e}')

    def switch_bottom_right_view(self):
        try:
            if not self.isTradeFeed:
                self.stack.setCurrentWidget(self.trade_feed_view)
                self.isTradeFeed = True
            else:
                self.stack.setCurrentWidget(self.personal_view)
                self.isTradeFeed = False
        except Exception as e:
            print(f'error switching bottom right view: {e}')

    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def mousePressEvent(self, event: QMouseEvent):
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

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.moving:
            delta = event.globalPos() - self.mouse_pos
            self.move(self.frame_pos + delta)
        elif self.resizing:
            self.resize_window(event.globalPos())

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

    def moveEvent(self, event):
        try:
            super().moveEvent(event)
            if self.accounts_popup is not None:
                self.move_accounts_popup()
            if self.personal_view.new_trade_popup is not None:
                self.personal_view.center_new_trade_popup()
        except Exception as e:
            print(f'Failed to move event: {e}')

    def move_accounts_popup(self):
        button_pos = self.accounts_list_button.mapToGlobal(self.accounts_list_button.rect().bottomLeft())
        popup_x = button_pos.x() - int(self.accounts_list_button.width() * 2)
        popup_y = button_pos.y()
        self.accounts_popup.move(popup_x, popup_y)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_stylesheet(app):
    stylesheet_path = resource_path('resources/style.qss')
    with open(stylesheet_path, "r") as file:
        app.setStyleSheet(file.read())


def main():
    app = QApplication(sys.argv)
    load_stylesheet(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
