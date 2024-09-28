from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import *
from SQL import get_all_accounts, insert_account, UserSession


class AccountsPopup(QDialog):
    account_changed = pyqtSignal([int, str, str])

    def __init__(self, parent=None, width=None, height=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.user_id = UserSession().get_user_id()
        self.setAttribute(Qt.WA_TranslucentBackground)

        if width:
            self.setFixedWidth(width)
        if height:
            self.setMaximumHeight(height)

        self.layout = QVBoxLayout()

        self.add_account_button = QPushButton('Add Account')
        self.add_account_button.clicked.connect(self.add_account_pressed)
        self.layout.addWidget(self.add_account_button)

        self.bottom_stack = QStackedWidget()

        self.account_list_scroll_area = QScrollArea()
        self.account_list_scroll_area.setWidgetResizable(True)
        self.account_list_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.account_list_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.account_list_scroll_area_widget = QWidget()
        self.account_list_scroll_area_layout = QVBoxLayout(self.account_list_scroll_area_widget)
        self.account_list_scroll_area_widget.setLayout(self.account_list_scroll_area_layout)
        self.account_list_scroll_area.setWidget(self.account_list_scroll_area_widget)

        self.create_account_frame = QFrame()
        self.create_account_layout = QVBoxLayout(self.create_account_frame)
        self.create_account_frame.setLayout(self.create_account_layout)

        self.account_type_list = QComboBox()
        self.account_type_list.addItem('Account Type')
        self.account_type_list.addItems(['Manual', 'NinjaTrader'])
        self.account_type_list.setCurrentIndex(0)
        self.account_type_list.model().item(0).setEnabled(False)

        self.account_name_entry = QLineEdit()
        self.account_name_entry.setPlaceholderText('Enter a Name')

        self.create_account_button = QPushButton('Create Account', clicked=self.create_account_pressed)

        self.create_account_layout.addWidget(self.account_type_list)
        self.create_account_layout.addWidget(self.account_name_entry)
        self.create_account_layout.addWidget(self.create_account_button)

        self.bottom_stack.addWidget(self.account_list_scroll_area)
        self.bottom_stack.addWidget(self.create_account_frame)
        self.account_list_scroll_area_widget.setStyleSheet("background-color: #222222;")

        self.layout.addWidget(self.bottom_stack)

        self.setLayout(self.layout)
        self.update_account_list()

    def update_account_list(self):
        try:
            clear_layout(self.account_list_scroll_area_layout)
            accounts = get_all_accounts(self.user_id)
            if accounts:
                for account_id, account_name, account_type in accounts:
                    name = account_name
                    if 'Apex' in account_name:
                        parts = account_name.split('-')
                        account_name = f'{parts[2]}-{parts[-1].split("!")[0]}'
                    button = QPushButton(account_name, self)
                    button.clicked.connect(lambda _, acc_id=account_id, acc=name, acc_t=account_type: self.account_changed.emit(acc_id, acc, acc_t))
                    button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")
                    self.account_list_scroll_area_layout.addWidget(button)

                self.bottom_stack.setCurrentWidget(self.account_list_scroll_area)
            else:
                self.add_account_button.setVisible(False)
                self.bottom_stack.setCurrentWidget(self.create_account_frame)
                print('No Accounts')
        except Exception as e:
            print(f'Failed to update account list: {e}')

    def add_account_pressed(self):
        try:
            self.add_account_button.setText('Go Back')
            self.add_account_button.clicked.disconnect()
            self.add_account_button.clicked.connect(self.go_back_pressed)
            self.bottom_stack.setCurrentWidget(self.create_account_frame)
        except Exception as e:
            print(f'Add account button did not work: {e}')

    def go_back_pressed(self):
        try:
            self.add_account_button.setVisible(True)
            self.add_account_button.setText('Add Account')
            self.add_account_button.clicked.disconnect()
            self.add_account_button.clicked.connect(self.add_account_pressed)
            self.bottom_stack.setCurrentWidget(self.account_list_scroll_area)
            self.update_account_list()
        except Exception as e:
            print(f'Failed to use go back action: {e}')

    def create_account_pressed(self):
        try:
            account_name = self.account_name_entry.text()
            account_type = self.account_type_list.currentText()
            if account_name and account_type != 'Account Type':
                insert_account(self.user_id, account_name, account_type)
                self.go_back_pressed()
                print(f'User {self.user_id} has created a new account called *{account_name}*, with the *{account_type}* type')
            else:
                print('Account name or account type cannot be blank.')
        except Exception as e:
            print(f'Create account pressed failed: {e}')


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
