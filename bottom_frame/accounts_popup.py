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

        self.select_account_type = None

        if width:
            self.setMaximumWidth(width)
        if height:
            self.setMaximumHeight(height)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0,0)
        self.setStyleSheet("background: rgba(34, 34, 34, 0);")

        self.account_types_button = QPushButton('Back', clicked=self.account_types_button_pressed)
        self.account_types_button.setStyleSheet("""
                        QPushButton:hover {
                            background-color: #ff4c4c;
                        }
                        QPushButton {
                            border: 2px solid #ff7f7f;
                        }""")


        self.add_account_button = QPushButton('Add Account', clicked=self.add_account_pressed)
        self.add_account_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #f7e334;
                    }
                    QPushButton {
                        border: 2px solid #f4e66e;
                    }""")

        self.bottom_stack = QStackedWidget()

        self.account_list_scroll_area = QScrollArea()
        self.account_list_scroll_area.setWidgetResizable(True)
        self.account_list_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.account_list_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.account_list_scroll_area_widget = QWidget()
        self.account_list_scroll_area_layout = QHBoxLayout(self.account_list_scroll_area_widget)
        self.account_list_scroll_area_widget.setLayout(self.account_list_scroll_area_layout)
        self.account_list_scroll_area.setWidget(self.account_list_scroll_area_widget)

        self.create_account_frame = QFrame()
        self.create_account_layout = QHBoxLayout(self.create_account_frame)
        self.create_account_frame.setLayout(self.create_account_layout)

        self.account_type_label = QLabel()
        self.account_type_label.setStyleSheet('color: white;')

        self.account_name_entry = QLineEdit()
        self.account_name_entry.setPlaceholderText('Name..')
        self.account_name_entry.setStyleSheet('color: white;')

        self.create_account_button = QPushButton('Create Account', clicked=self.create_account_pressed)
        self.set_button_style(self.create_account_button)

        self.create_account_layout.addWidget(self.account_type_label)
        self.create_account_layout.addWidget(self.account_name_entry)
        self.create_account_layout.addWidget(self.create_account_button)

        self.bottom_stack.addWidget(self.account_list_scroll_area)
        self.bottom_stack.addWidget(self.create_account_frame)
        self.account_list_scroll_area.setStyleSheet("background: rgba(34, 34, 34, 0);"
                                                    "border: none;")
        self.layout.addWidget(self.account_types_button)
        self.layout.addWidget(self.bottom_stack)
        self.layout.addWidget(self.add_account_button)

        self.setLayout(self.layout)
        self.account_options_view()

    def account_types_button_pressed(self):
        self.account_options_view()

    def set_button_style(self, button):
        button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }
                    QPushButton {
                        border: 2px solid #c3dc9b;;
                    }""")

    def account_options_view(self):
        try:
            clear_layout(self.account_list_scroll_area_layout)

            self.backtest_accounts_button = QPushButton('Backtest Accounts')
            self.ninjatrader_accounts_button = QPushButton('NinjaTrader Accounts')
            self.manual_accounts_button = QPushButton('Manual Accounts')

            for widgets in (self.backtest_accounts_button, self.ninjatrader_accounts_button, self.manual_accounts_button):
                if widgets == self.backtest_accounts_button:
                    def update_list():
                        self.select_account_type = 'Backtest'
                        self.account_list_view(button_acc_type='Backtest')
                    widgets.clicked.connect(update_list)
                elif widgets == self.ninjatrader_accounts_button:
                    def update_list():
                        self.select_account_type = 'NinjaTrader'
                        self.account_list_view(button_acc_type='NinjaTrader')
                    widgets.clicked.connect(update_list)
                elif widgets == self.manual_accounts_button:
                    def update_list():
                        self.select_account_type = 'Manual'
                        self.account_list_view(button_acc_type='Manual')
                    widgets.clicked.connect(update_list)
                self.account_list_scroll_area_layout.addWidget(widgets)
                self.set_button_style(widgets)

            self.bottom_stack.setCurrentWidget(self.account_list_scroll_area)
            self.account_types_button.setVisible(False)
            self.add_account_button.setVisible(False)
            if self.add_account_button.text() == 'Go Back':
                self.add_account_button.setText('Add Account')
                self.add_account_button.clicked.disconnect()
                self.add_account_button.clicked.connect(self.add_account_pressed)
        except Exception as e:
            print(f'Failed to setup account options: {e}')

    def account_list_view(self, button_acc_type=None):
        try:
            clear_layout(self.account_list_scroll_area_layout)
            accounts = get_all_accounts(self.user_id, account_type=button_acc_type)
            print(accounts)
            if accounts:
                for account_id, account_name, account_type in accounts:
                    if account_type == button_acc_type:
                        name = account_name
                        if 'Apex' in account_name:
                            parts = account_name.split('-')
                            account_name = f'{parts[2]}-{parts[-1].split("!")[0]}'
                        button = QPushButton(account_name, self)
                        button.clicked.connect(lambda _, acc_id=account_id, acc=name, acc_t=account_type: self.account_name_selected(acc_id, acc, acc_t))
                        self.set_button_style(button)
                        self.account_list_scroll_area_layout.addWidget(button)

                self.bottom_stack.setCurrentWidget(self.account_list_scroll_area)
                self.account_types_button.setVisible(True)
                self.add_account_button.setVisible(True)
            else:
                self.add_account_button.setVisible(True)
                self.account_types_button.setVisible(True)
                self.add_account_pressed()
                print('No Accounts')
        except Exception as e:
            print(f'Failed to update account list: {e}')

    def account_name_selected(self, acc_id, acc, acc_t):
        self.account_changed.emit(acc_id, acc, acc_t)
        self.account_options_view()


    def add_account_pressed(self):
        try:
            self.add_account_button.setText('Go Back')
            self.add_account_button.clicked.disconnect()
            self.add_account_button.clicked.connect(self.go_back_pressed)

            acc_type = self.return_type()
            self.account_type_label.setText(f'{acc_type} Account:')
            self.bottom_stack.setCurrentWidget(self.create_account_frame)
        except Exception as e:
            print(f'Add account button did not work: {e}')

    def return_type(self):
        print(self.select_account_type)
        if self.select_account_type == 'Manual':
            return 'Manual'
        elif self.select_account_type == 'NinjaTrader':
            return 'NinjaTrader'
        elif self.select_account_type == 'Backtest':
            return 'Backtest'

    def go_back_pressed(self):
        try:
            self.add_account_button.setVisible(True)
            self.add_account_button.setText('Add Account')
            self.add_account_button.clicked.disconnect()
            self.add_account_button.clicked.connect(self.add_account_pressed)
            self.bottom_stack.setCurrentWidget(self.account_list_scroll_area)
            # self.account_list_view()
        except Exception as e:
            print(f'Failed to use go back action: {e}')

    def create_account_pressed(self):
        try:
            account_name = self.account_name_entry.text()
            account_type = self.account_type_label.text()
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
