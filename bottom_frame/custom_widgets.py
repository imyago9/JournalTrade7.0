import os
from datetime import datetime

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, Qt, pyqtSignal
import pandas as pd
from SQL import get_trade_note, insert_daily_note, update_trade_note, get_trades_for_account, insert_trade


class CustomCalendar(QWidget):
    day_clicked = pyqtSignal(int, str)

    def __init__(self, account_type='NinjaTrader', parent=None, money_visible=False):
        super(CustomCalendar, self).__init__(parent)
        self.account_type = account_type
        self.account_id = None
        self.money_visible = money_visible

        self.layout = QVBoxLayout(self)

        self.date_edit_layout = QHBoxLayout()
        self.init_dateedits()
        self.layout.addLayout(self.date_edit_layout)

        self.navigation_layout = QHBoxLayout()
        self.init_navigation()
        self.layout.addLayout(self.navigation_layout)

        self.calendar_layout = QGridLayout()
        self.layout.addLayout(self.calendar_layout)

        self.dates = {}
        self.current_date = QDate.currentDate()
        self.self = self

        self.initUI()
        self.setDate(self.current_date.year(), self.current_date.month())

        self.account_data = {}

        self.layout.setStretch(0, 1)
        self.layout.setStretch(1, 6)

    def init_dateedits(self):
        self.fde = QDateEdit()
        self.fde.setCalendarPopup(True)
        self.fde.setStyleSheet("""QDateEdit {
                                background-color: #222222;
                                color: white;
                                border: 1px solid #c3dc9b;
                                border-radius: 4px;
                            }
                            
                            QDateEdit::drop-down {
                                background-color: #c3dc9b;
                                border: none;
                                subcontrol-position: left;
                            }
                            
                            QDateEdit::down-arrow {
                                image: none;
                                background-color: #c3dc9b;
                                border: 1px solid #c3dc9b;
                                border-radius: 5px;
                            }
                            QDateEdit::down-arrow:hover {
                                image: none;
                                background-color: #222222;
                                border: 1px solid #222222;
                                border-radius: 5px;
                            }
                            
                            QCalendarWidget QWidget#qt_calendar_navigationbar {
                                background-color: #222222;
                                color: white;
                            }
                            
                             QCalendarWidget QToolButton {
                                background-color: #222222;
                                color: white;
                            }
                            
                            QCalendarWidget QToolButton:hover {
                                background-color: #333333;
                            }
                            
                            QCalendarWidget QAbstractItemView {
                                selection-background-color: #c3dc9b;
                                selection-color: black;
                            }""")
        self.sde = QDateEdit()
        self.sde.setCalendarPopup(True)
        self.sde.setStyleSheet("""QDateEdit {
                                background-color: #222222;
                                color: white;
                                border: 1px solid #c3dc9b;
                                border-radius: 4px;
                            }
                            
                            QDateEdit::drop-down {
                                background-color: #c3dc9b;
                                border: none;
                                subcontrol-position: right;
                            }
                            
                            QDateEdit::down-arrow {
                                image: none;
                                background-color: #c3dc9b;
                                border: 1px solid #c3dc9b;
                                border-radius: 5px;
                            }
                            QDateEdit::down-arrow:hover {
                                image: none;
                                background-color: #222222;
                                border: 1px solid #222222;
                                border-radius: 5px;
                            }
                            
                            QCalendarWidget QWidget#qt_calendar_navigationbar {
                                background-color: #222222;
                                color: white;
                            }
                            
                             QCalendarWidget QToolButton {
                                background-color: #222222;
                                color: white;
                            }
                            
                            QCalendarWidget QToolButton:hover {
                                background-color: #333333;
                            }
                            
                            QCalendarWidget QAbstractItemView {
                                selection-background-color: #c3dc9b;
                                selection-color: black;
                            }""")
        self.date_edit_layout.addStretch()
        sd_label = QLabel('Start Date')
        sd_label.setStyleSheet('border: none; color: white;')
        ed_label = QLabel('End Date')
        ed_label.setStyleSheet('border: none; color: white;')
        self.date_edit_layout.addWidget(sd_label)
        self.date_edit_layout.addWidget(self.fde)
        self.date_edit_layout.addWidget(self.sde)
        self.date_edit_layout.addWidget(ed_label)
        self.date_edit_layout.addStretch()

    def init_navigation(self):

        self.prev_button = QPushButton("<", self)
        self.prev_button.clicked.connect(self.prevMonth)
        self.navigation_layout.addWidget(self.prev_button)

        self.current_month_label = QLabel(self)
        self.current_month_label.setStyleSheet('border: none; color: white;')
        self.navigation_layout.addWidget(self.current_month_label)

        self.next_button = QPushButton(">", self)
        self.next_button.clicked.connect(self.nextMonth)
        self.navigation_layout.addWidget(self.next_button)

    def initUI(self):
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", 'Sun']

        for i, day in enumerate(days_of_week):
            day_label = QLabel(day)
            day_label.setStyleSheet('border: none; color: white;')
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.calendar_layout.addWidget(day_label, 0, i)

        for row in range(1, 7):
            self.calendar_layout.setRowStretch(row, 1)
            for col in range(7):
                each_day_frame = ClickableFrame(self)
                date_label, profit_value, trade_number = each_day_frame.get_labels()

                self.calendar_layout.addWidget(each_day_frame, row, col)

                self.dates[(row, col)] = (date_label, profit_value, trade_number)

                self.calendar_layout.setColumnStretch(col, 1)

    def setDate(self, year, month):
        self.current_month_label.setText(f"{QDate.longMonthName(month)} {year}")
        self.current_month_label.setAlignment(Qt.AlignCenter)
        self.current_month_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        date = QDate(year, month, 1)
        day_of_week = date.dayOfWeek() - 1

        for (row, col), (date_label, profit_label, trade_label) in self.dates.items():
            date_label.setText("")
            profit_label.setText("")
            trade_label.setText("")
            date_label.parent().setStyleSheet("""
                                border: none;
                                border-radius: none;
                                background-color: none;
                            """)

        row = 1
        col = day_of_week
        while date.month() == month:
            if col < 7:
                self.dates[(row, col)][0].setText(str(date.day()))
                self.dates[(row, col)][0].parent().setStyleSheet("""
                                border: 2px solid #c3dc9b;
                                border-radius: 5px;
                                background-color: #333333;
                            """)
                col += 1
            date = date.addDays(1)
            if col >= 7:
                col = 0
                row += 1

    def setColoredText(self, day, profit, trades):
        try:
            for (row, col), (date_label, profit_label, trades_label) in self.dates.items():
                if date_label.text() == str(day):
                    if trades == 0:
                        date_label.setStyleSheet("color: #8f7b7b; border: none;")
                    else:
                        profit_color = '#c3dc9b' if int(profit) > 0 else ('#ff4c4c' if int(profit) < 0 else 'white')
                        profit = abs(profit) if self.money_visible else '---'
                        date_label.setText(str(day))
                        date_label.setStyleSheet("color: white; border: none;")
                        profit_label.setText(f'{profit}')
                        profit_label.setStyleSheet(f"color: {profit_color}; font-weight: bold; border: none;")
                        trades_label.setText(f"{trades}'Ts")
                        trades_label.setStyleSheet("color: white; border: none;")
                    break
        except Exception as e:
            print(f'Error setting colored calendar text: {e}')

    def update_calendar(self, data):
        try:
            if self.account_type == 'NinjaTrader':
                time_column_name = 'EntryT'
            elif self.account_type == 'Manual':
                time_column_name = 'entry_time'
            data = data
            data = data.groupby(time_column_name).agg({'profit': 'sum', 'direction': 'first'}).reset_index()

            data[time_column_name] = pd.to_datetime(data[time_column_name])
            data['Date'] = data[time_column_name].dt.date
            grouped_data = data.groupby('Date').agg({
                'profit': 'sum',
                time_column_name: 'count'
            }).rename(columns={time_column_name: 'Trades'}).reset_index()

            last_day_of_month = QDate(self.current_date.year(), self.current_date.month(), 1).addMonths(1).addDays(
                -1).day()

            for day in range(1, last_day_of_month + 1):
                date_to_check = QDate(self.current_date.year(), self.current_date.month(), day)
                date_str = date_to_check.toString("yyyy-MM-dd")
                date_to_check_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                if date_to_check_date in grouped_data['Date'].values:
                    row = grouped_data[grouped_data['Date'] == date_to_check_date]
                    profit = row['profit'].values[0]
                    trades = row['Trades'].values[0]
                    self.setColoredText(day, profit, trades)
                else:
                    self.setColoredText(day, 0, 0)

        except Exception as e:
            print(f'Failed to update calendar: {e}')

    def prevMonth(self):
        self.current_date = self.current_date.addMonths(-1)
        self.setDate(self.current_date.year(), self.current_date.month())
        self.update_calendar(self.account_data)

    def nextMonth(self):
        self.current_date = self.current_date.addMonths(1)
        self.setDate(self.current_date.year(), self.current_date.month())
        self.update_calendar(self.account_data)

    def wheelEvent(self, event):
        # Check the direction of the scroll
        if event.angleDelta().y() > 0:
            self.prevMonth()  # Scroll up: Go to the previous month
        else:
            self.nextMonth()  # Scroll down: Go to the next month


class ClickableFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.date_label = QLabel("")
        self.date_label.setStyleSheet("border: none;")
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.profit_value = QLabel("")
        self.profit_value.setStyleSheet("border: none;")
        self.profit_value.setAlignment(Qt.AlignCenter)
        self.profit_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.trade_number = QLabel("")
        self.trade_number.setStyleSheet("border: none;")
        self.trade_number.setAlignment(Qt.AlignCenter)
        self.trade_number.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(self.date_label)
        layout.addWidget(self.profit_value)
        layout.addWidget(self.trade_number)
        self.setLayout(layout)

    def get_labels(self):
        return self.date_label, self.profit_value, self.trade_number

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        try:
            parent = self.parent()
            parent.day_clicked.emit(parent.account_id,
                                    str(f'{parent.current_date.year()}-{parent.current_date.month():02d}-{int(self.date_label.text()):02d}'))
        except Exception as e:
            print(f'Failed mouse press event: {e}')


class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.type = type
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        try:
            if self.pixmap() is not None:
                self.parent().set_screenshot_first_stack()
        except Exception as e:
            print(f'Failed mouse press event: {e}')


class LimitedTextEdit(QTextEdit):
    def __init__(self, char_limit, *args, **kwargs):
        super(LimitedTextEdit, self).__init__(*args, **kwargs)
        self.char_limit = char_limit

    def keyPressEvent(self, event):
        if len(self.toPlainText()) >= self.char_limit and event.key() not in (Qt.Key_Backspace, Qt.Key_Delete):
            # Ignore the key press if the character limit is reached
            event.ignore()
        else:
            super(LimitedTextEdit, self).keyPressEvent(event)

    def insertFromMimeData(self, source):
        # Also handle paste operations
        if len(self.toPlainText()) + len(source.text()) > self.char_limit:
            return
        super(LimitedTextEdit, self).insertFromMimeData(source)


class CustomNoteView(QWidget):
    go_back_button_pressed = pyqtSignal()

    def __init__(self, parent=None, trade_id=None, account_id=None, date=None, type=None):
        super(CustomNoteView, self).__init__(parent)
        self.trade_id = trade_id
        self.account_id = account_id
        self.note_date = date
        self.first_date = None
        self.second_date = None
        if self.trade_id:
            self.server_note_id, self.server_note, self.server_created_at = get_trade_note(trade_id=trade_id)
        if self.account_id and self.note_date:
            self.server_note_id, self.server_note, self.server_created_at = get_trade_note(account_id=account_id,
                                                                                           date=date)

        self.setupView()
        if self.server_note is not None:
            self.notes_entry_box.setText(str(self.server_note))
            self.notes_entry_box.setStyleSheet("""
            QWidget {
                background-color: #222222;
                color: white;
                border: none;
                outline: none;
            }
        """)
        self.setStyleSheet("""
            QWidget {
                background-color: #222222;
                color: white;
            }
        """)

    def setTitle(self):
        title_label = f'Trade Notes:\n' if self.trade_id else f'Daily Notes:\n' if self.account_id else ""
        self.title.setText(title_label)
        self.title.setStyleSheet('color: white;')

    def setupView(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.notes_frame = QFrame()
        self.notes_layout = QVBoxLayout(self.notes_frame)
        self.title = QLabel()
        self.setTitle()
        self.title.setAlignment(Qt.AlignCenter)
        self.notes_entry_box = LimitedTextEdit(char_limit=500)
        if self.account_id:
            def confirm_pressed():
                try:
                    self.save_button.setText('Save Daily Note')
                    self.save_button.disconnect()
                    self.save_button.clicked.connect(save_button_pressed)

                    self.go_back_button.setText('Go Back')
                    self.go_back_button.disconnect()
                    self.go_back_button.clicked.connect(emit_back_signal)
                    if self.server_note_id:
                        self.setTitle()
                        update_trade_note(self.server_note_id, self.notes_entry_box.toPlainText(), note_type='daily')
                    else:
                        insert_daily_note(self.account_id, self.notes_entry_box.toPlainText(), self.note_date)
                    self.notes_entry_box.setStyleSheet("""
                        QWidget {
                            background-color: #222222;
                            color: white;
                            border: none;
                            outline: none;
                        }
                    """)
                except Exception as e:
                    print(f'Failed to press confirm button: {e}')

            def cancel_pressed():
                self.save_button.setText('Save Daily Note')
                self.save_button.disconnect()
                self.save_button.clicked.connect(save_button_pressed)

                self.go_back_button.setText('Go Back')
                self.go_back_button.disconnect()
                self.go_back_button.clicked.connect(emit_back_signal)
                if self.server_note_id:
                    self.setTitle()

            def save_button_pressed():
                try:
                    self.save_button.setText('Confirm')
                    self.save_button.disconnect()
                    self.save_button.clicked.connect(confirm_pressed)
                    self.go_back_button.setText('Cancel')
                    self.go_back_button.disconnect()
                    self.go_back_button.clicked.connect(cancel_pressed)
                    if self.server_note_id:
                        self.title.setText('Replace existing note?')
                        self.title.setStyleSheet('color: #ff4c4c;')
                except Exception as e:
                    print(f'Failed to press save button: {e}')

            def emit_back_signal():
                try:
                    self.go_back_button_pressed.emit()
                except Exception as e:
                    print(f'Failed to emit back signal: {e}')

            self.go_back_button = QPushButton('Go Back', clicked=emit_back_signal)
            self.go_back_button.setStyleSheet("""
                        QPushButton:hover {
                            background-color: #ff4c4c;
                        }
                        QPushButton {
                            border: 2px solid #ff7f7f;
                        }""")

            self.notes_layout.addWidget(self.go_back_button)
            self.save_button = QPushButton('Save Daily Note', clicked=save_button_pressed)
            self.save_button.setStyleSheet("""
                        QPushButton:hover {
                            background-color: #2c7e33;
                        }""")
            self.notes_layout.addWidget(self.save_button)
        self.notes_layout.addWidget(self.title)
        self.notes_layout.addWidget(self.notes_entry_box)
        layout.addWidget(self.notes_frame)
        if self.server_note:
            self.notes_entry_box.setText(self.server_note)

    def get_note_text(self):
        return self.notes_entry_box.toPlainText()


class FiledropFrame(QFrame):
    trade_created = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cancel_button = None
        self.confirm_button = None
        self.label = None
        self.new_trades_to_insert_verification = False
        self.grouped_trades_verification = False
        self.new_trades_to_insert = None
        self.grouped_trades = None
        self.account_name = None
        self.account_id = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # Accept only if the file is a CSV
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.csv'):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.csv'):
                    self.check_for_new_trades(file_path)
                    event.acceptProposedAction()
                else:
                    self.setText("Only CSV files are allowed")
        else:
            event.ignore()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        print('A beat do necklace')

    def check_for_new_trades(self, file_name):
        if not os.path.exists(file_name) or os.stat(file_name).st_size == 0:
            print('Missing or empty data inside csv. Please import data as instructed and try again.')
            return
        new_trades = pd.read_csv(file_name)
        required_columns = {
            'Instrument': 'instrument',
            'Account': 'account',
            'Market pos.': 'direction',
            'Qty': 'quantity',
            'Entry price': 'entry_price',
            'Exit price': 'exit_price',
            'Entry time': 'entry_time',
            'Exit time': 'exit_time',
            'Profit': 'profit',
            'Commission': 'com'
        }
        missing_columns = set(required_columns.keys()) - set(new_trades.columns)
        if missing_columns:
            self.label.setText(f'Missing required columns: {missing_columns}')
            print(f'Missing required columns: {missing_columns}')
            return

        new_trades.rename(columns=required_columns, inplace=True)
        new_trades = new_trades[list(required_columns.values())]

        columns_to_modify = ['profit', 'com']
        for column in columns_to_modify:
            new_trades[column] = new_trades[column].astype(str).str.replace(r'[$,)]',
                                                                            '', regex=True).str.replace(r'\(', '-',
                                                                                                        regex=True)
            new_trades[column] = new_trades[column].astype(float).round(2)

        for column in ['entry_time', 'exit_time']:
            new_trades[column] = pd.to_datetime(new_trades[column], errors='coerce')

        new_trades = new_trades[new_trades['account'] == self.account_name]
        if new_trades.empty:
            self.label.setText('No trades found for this account.')
            print(f"No trades found for account '{self.account_name}' in the CSV file.")
            return

        self.grouped_trades = group_trades_by_entry_time(new_trades)

        existing_trades = get_trades_for_account(self.account_id)
        if existing_trades:
            # Convert existing trades to a DataFrame for easy comparison
            existing_trades_df = pd.DataFrame(existing_trades)

            # Compare entry times to find new trades
            last_entry_time = existing_trades_df['entry_time'].max()
            self.new_trades_to_insert = self.grouped_trades[self.grouped_trades['entry_time'] > last_entry_time]

            if self.new_trades_to_insert.empty:
                self.label.setText('No new trades to update.')
                self.cancel_button.setVisible(True)
                self.cancel_button.clicked.connect(self.cancel_button_pressed)
                self.confirm_button.setVisible(True)
                self.confirm_button.clicked.connect(self.confirm_button_pressed)
                print("No new trades to update.")
                print(existing_trades)
            else:
                self.label.setText(f'Found {len(self.new_trades_to_insert)} new trade(s) to insert.')
                print(f"Found {len(self.new_trades_to_insert)} new trade(s) to insert.")
                self.new_trades_to_insert_verification = True
                self.cancel_button.setVisible(True)
                self.confirm_button.setVisible(True)
                self.confirm_button.clicked.connect(self.confirm_button_pressed)
                self.cancel_button.clicked.connect(self.cancel_button_pressed)

        else:
            self.label.setText('Save trades for the first time?')
            print('No existing trades found. Saving all trades as new trades.')
            self.grouped_trades_verification = True
            self.cancel_button.setVisible(True)
            self.confirm_button.setVisible(True)
            self.confirm_button.clicked.connect(self.confirm_button_pressed)
            self.cancel_button.clicked.connect(self.cancel_button_pressed)

    def confirm_button_pressed(self):
        if self.new_trades_to_insert is not None and self.new_trades_to_insert_verification:
            self.save_new_trades_to_db(self.new_trades_to_insert)
            self.trade_created.emit(self.account_id)
            self.new_trades_to_insert_verification = False
            self.cancel_button.setVisible(False)
            self.confirm_button.setVisible(False)
        elif self.grouped_trades is not None and self.grouped_trades_verification:
            self.save_new_trades_to_db(self.grouped_trades)
            self.trade_created.emit(self.account_id)
            self.grouped_trades_verification = False
            self.cancel_button.setVisible(False)
            self.confirm_button.setVisible(False)
        else:
            self.label.setText('Please select a valid csv file.')

    def cancel_button_pressed(self):
        self.label.setText('Drag csv file here to update trades.\n'
                           '(Click to browse computer files.)')
        self.new_trades_to_insert = None
        self.new_trades_to_insert_verification = None
        self.grouped_trades = None
        self.grouped_trades_verification = None
        self.cancel_button.setVisible(False)
        self.confirm_button.setVisible(False)
        self.cancel_button.disconnect()
        self.confirm_button.disconnect()

    def save_new_trades_to_db(self, grouped_trades):
        try:
            for _, trade in grouped_trades.iterrows():
                instrument = trade['instrument'].split()[0]

                entries = [(trade['entry_price'], trade['quantity'])]
                exits = [(trade['exit_price'], trade['quantity'])]

                trade_id = insert_trade(
                    self.account_id,
                    instrument,
                    trade['direction'],
                    entries,
                    exits,
                    trade['entry_time'],
                    trade['exit_time'],
                    trade['profit'],
                    trade['com']
                )

                if trade_id:
                    print(f"Trade ID {trade_id} inserted successfully for instrument {instrument}.")
                else:
                    print(f"Failed to insert trade for {instrument} at {trade['entry_time']}")

        except Exception as e:
            print(f"Error saving new trades: {e}")


def group_trades_by_entry_time(data):
    # Group by entry_time
    grouped_data = data.groupby('entry_time').agg(
        {
            'exit_time': 'last',  # Take the last exit time
            'instrument': 'first',  # Assuming all rows have the same instrument, take the first
            'direction': 'first',  # Assuming direction is the same, take the first
            'entry_price': lambda x: (x * data.loc[x.index, 'quantity']).sum() / data.loc[x.index, 'quantity'].sum(),
            # Weighted average entry price
            'exit_price': lambda x: (x * data.loc[x.index, 'quantity']).sum() / data.loc[x.index, 'quantity'].sum(),
            # Weighted average exit price
            'quantity': 'sum',  # Sum up the quantities
            'profit': 'sum',  # Sum up the profit
            'com': 'sum'  # Sum up the commissions
        }
    ).reset_index()

    return grouped_data
