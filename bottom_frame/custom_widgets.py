from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, Qt, pyqtSignal
import pandas as pd
from SQL import get_trade_note, insert_daily_note, update_trade_note


class CustomCalendar(QWidget):
    day_clicked = pyqtSignal(int, str)
    def __init__(self, account_type='NinjaTrader', parent=None):
        super(CustomCalendar, self).__init__(parent)
        self.setStyleSheet("""background-color: #222222;""")
        self.setStyleSheet("""color: white;""")

        self.layout = QVBoxLayout(self)
        self.navigation_layout = QHBoxLayout()
        self.account_type = account_type
        self.account_id = None

        self.prev_button = QPushButton("<", self)
        self.prev_button.clicked.connect(self.prevMonth)
        self.navigation_layout.addWidget(self.prev_button)

        self.current_month_label = QLabel(self)
        self.navigation_layout.addWidget(self.current_month_label)

        self.next_button = QPushButton(">", self)
        self.next_button.clicked.connect(self.nextMonth)
        self.navigation_layout.addWidget(self.next_button)

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

    def initUI(self):
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", 'Sun']

        for i, day in enumerate(days_of_week):
            day_label = QLabel(day)
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

        row = 1
        col = day_of_week
        while date.month() == month:
            if col < 7:
                self.dates[(row, col)][0].setText(str(date.day()))
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
                        date_label.setText(str(day))
                        date_label.setStyleSheet("color: white; border: none;")
                        profit_label.setText(f'{abs(profit)}')
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

class ClickableFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            border: 2px solid #c3dc9b;
            border-radius: 5px;
            background-color: #333333;
        """)
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
                parent.day_clicked.emit(parent.account_id, str(f'{parent.current_date.year()}-{parent.current_date.month()}-{int(self.date_label.text())}'))
        except Exception as e:
            print(f'Failed mouse press event: {e}')


class ClickableLabel(QLabel):
    def __init__(self, parent=None, type=None):
        super().__init__(parent)
        self.type = type
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        try:
            if self.pixmap() is not None:
                if self.type == 'ti_ss':
                    self.parent().set_screenshot_first_stack()
            if self.type == 'day_label':
                day = int(self.text())
                custom_calendar = self.parent()
                if custom_calendar:
                    custom_calendar.day_clicked.emit(custom_calendar.account_id,
                                                QDate(custom_calendar.current_date.year(), custom_calendar.current_date.month(), day))
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
    go_back_button_pressed = pyqtSignal(QDate, QDate)
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
                    self.go_back_button_pressed.emit(self.first_date, self.second_date)
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