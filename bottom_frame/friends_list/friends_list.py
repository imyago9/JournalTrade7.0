from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from SQL import *


class FriendsList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.setup_friend_list()
        self.user_id = UserSession().get_user_id()
        self.setStyleSheet("""
        QWidget {
            background-color: #222222;
            color: white;
        }""")

    def setup_friend_list(self):
        self.menu_title = QLabel("Friend's List")
        self.main_layout.addWidget(self.menu_title)
        self.add_friend_button = QPushButton("Add Friend", clicked=self.add_friend)
        self.main_layout.addWidget(self.add_friend_button)
        self.add_friend_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")

        self.requests_button = QPushButton("Requests", clicked=self.check_requests)
        self.main_layout.addWidget(self.requests_button)
        self.requests_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")

        self.stack = QStackedWidget()


        self.friend_list_frame = QFrame()
        self.friend_list_layout = QVBoxLayout(self.friend_list_frame)
        self.friend_list_layout.setContentsMargins(0, 0, 0, 0)
        self.friend_list_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content.setLayout(self.scroll_content_layout)
        self.scroll_area.setWidget(self.scroll_content)

        self.friend_list_layout.addWidget(self.scroll_area)
        self.friend_list_layout.setStretch(0, 1)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.friend_request_list_frame = QFrame()
        self.friend_request_list_layout = QVBoxLayout(self.friend_request_list_frame)
        self.friend_request_list_layout.setContentsMargins(0, 0, 0, 0)
        self.friend_request_list_layout.setSpacing(0)

        self.request_scroll_area = QScrollArea()
        self.request_scroll_area.setWidgetResizable(True)
        self.request_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.request_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.request_scroll_area.setFrameStyle(QFrame.NoFrame)
        self.request_scroll_content = QWidget()
        self.request_scroll_content_layout = QVBoxLayout(self.request_scroll_content)
        self.request_scroll_content.setLayout(self.request_scroll_content_layout)
        self.request_scroll_area.setWidget(self.request_scroll_content)

        self.friend_request_list_layout.addWidget(self.request_scroll_area)
        self.friend_request_list_layout.setStretch(0, 1)
        self.request_scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.stack.addWidget(self.friend_list_frame)
        self.stack.addWidget(self.friend_request_list_frame)
        self.stack.setCurrentWidget(self.friend_list_frame)
        self.main_layout.addWidget(self.stack)

    def update_friends_list(self):
        for i in reversed(range(self.scroll_content_layout.count())):
            widget = self.scroll_content_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        friends = get_friends(self.user_id)
        for friend in friends:
            user_id, username = friend
            friend_label = QLabel(username)
            self.scroll_content_layout.addWidget(friend_label)

    def update_friend_request_list(self):
        try:
            friends_id = get_received_friend_requests(self.user_id)
            for i in reversed(range(self.request_scroll_content_layout.count())):
                widget = self.request_scroll_content_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)

            if not friends_id:
                print('No friend requests available.')
            else:
                user_ids = [friend[0] for friend in friends_id]
                friends_username = get_username_by_userid(user_ids)
                print(friends_username)
                for friend, friend_id in zip(friends_username, user_ids):
                    friend_label = QLabel('✦ ' + friend)
                    accept_request_button = QPushButton('Accept')
                    accept_request_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")
                    accept_request_button.clicked.connect(lambda _, fid=friend_id: self.accept_request_action(fid, self.user_id))
                    reject_request_button = QPushButton('Reject')
                    reject_request_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")
                    reject_request_button.clicked.connect(lambda _, fid=friend_id: self.reject_request_action(fid, self.user_id))
                    hbox = QVBoxLayout()
                    hbox.setAlignment(Qt.AlignVCenter)
                    hbox.addWidget(accept_request_button)
                    hbox.addWidget(reject_request_button)
                    hbox.setSpacing(5)
                    vbox = QVBoxLayout()
                    vbox.setAlignment(Qt.AlignCenter)
                    vbox.addWidget(friend_label)
                    vbox.addLayout(hbox)
                    vbox.setContentsMargins(0, 0, 0, 0)
                    received_request_frame = QFrame()
                    received_request_frame.setLayout(vbox)
                    self.request_scroll_content_layout.addWidget(received_request_frame)
        except Exception as e:
            print(f'Error updating requests list: {e}')


    def accept_request_action(self, user_id, friend_id):
        accept_friend_request(user_id, friend_id)
        self.update_friend_request_list()

    def reject_request_action(self, user_id, friend_id):
        reject_friend_request(user_id, friend_id)
        self.update_friend_request_list()


    def add_friend(self):
        self.menu_title.setAlignment(Qt.AlignCenter)
        self.menu_title.setText('Add a Friend')
        self.friend_list_frame.hide()
        self.requests_button.hide()
        self.add_friend_button.hide()
        self.add_friend_text_entry = QLineEdit(self)
        self.add_friend_text_entry.setStyleSheet("border: 2px solid #c3dc9b;")
        self.add_friend_text_entry.setPlaceholderText("Enter friend's name")
        self.main_layout.insertWidget(2, self.add_friend_text_entry)
        self.send_request_button = QPushButton("Send Request", self)
        self.send_request_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")
        self.send_request_button.clicked.connect(self.send_request)
        self.main_layout.insertWidget(3, self.send_request_button)
        self.go_back_add_friend_button = QPushButton("Go Back", self)
        self.go_back_add_friend_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")
        self.go_back_add_friend_button.clicked.connect(self.go_back_add_friend)
        self.main_layout.insertWidget(4, self.go_back_add_friend_button)

    def go_back_add_friend(self):
        self.menu_title.setText("Friend's List")
        self.add_friend_text_entry.hide()
        self.send_request_button.hide()
        self.go_back_add_friend_button.hide()

        self.add_friend_button.show()
        self.friend_list_frame.show()
        self.requests_button.show()

    def send_request(self):
        try:
            friend_name = self.add_friend_text_entry.text()
            if friend_name:
                friend_id = username_to_userid(friend_name)
                if friend_id:
                    send_friend_request(self.user_id, friend_id)
                    print(f"Friend request sent to {friend_name}")
                self.go_back_add_friend()
        except Exception as e:
            print(f'Error sending friend request: {e}')

    def check_requests(self):
        self.menu_title.setText("Friend Requests")
        self.add_friend_button.hide()

        self.requests_button.setText('Go Back')
        self.requests_button.disconnect()
        self.requests_button.clicked.connect(self.go_back_requests)
        self.update_friend_request_list()
        self.stack.setCurrentWidget(self.friend_request_list_frame)

    def go_back_requests(self):
        self.menu_title.setText("Friend's List")
        self.add_friend_button.show()
        self.requests_button.setText('Requests')
        self.requests_button.disconnect()
        self.requests_button.clicked.connect(self.check_requests)
        self.stack.setCurrentWidget(self.friend_list_frame)
        self.update_friends_list()