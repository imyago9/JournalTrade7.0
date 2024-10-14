import pandas as pd
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
from PyQt5.QtWidgets import *
from SQL import *
from bottom_frame.image_drop import ImageDropArea


class ManualNewTradePopup(QDialog):
    trade_created = pyqtSignal(int)
    def __init__(self, parent=None, width=None, height=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.user_id = UserSession().get_user_id()
        self.account_id = None
        self.account_name = None
        self.setStyleSheet("""
        QWidget {
            background-color: #222222;
            color: white;
        }""")

        if width:
            self.setMaximumWidth(width)
        if height:
            self.setMaximumHeight(height)

        self.layout = QHBoxLayout()

        self.left_side_frame = QFrame()
        self.left_side_layout = QVBoxLayout(self.left_side_frame)

        self.instrument_label = QLabel('Instrument:')
        self.instrument_entry = QLineEdit()
        self.instrument_entry.setPlaceholderText('Ex: ES, NQ, etc..')

        self.direction_label = QLabel('Direction:')
        self.direction_entry = QComboBox()
        self.direction_entry.addItems(['Long', 'Short'])

        self.entry_price_quantity_label = QLabel('Entry Price & Qty')

        self.entry_price_quantity_frame = QFrame()
        self.entry_price_quantity_layout = QVBoxLayout(self.entry_price_quantity_frame)

        self.entry_price_quantity_row_frame = QFrame()
        self.entry_price_quantity_row_layout = QHBoxLayout(self.entry_price_quantity_row_frame)

        self.entry_price_entry = QDoubleSpinBox()
        self.entry_price_entry.setRange(0, 1000000)
        self.entry_price_entry.setDecimals(2)
        self.entry_price_quantity_row_layout.addWidget(self.entry_price_entry)

        self.entry_quantity_entry = QSpinBox()
        self.entry_quantity_entry.setRange(1, 1000000)
        self.entry_price_quantity_row_layout.addWidget(self.entry_quantity_entry)

        self.add_entry_price_quantity_slot = QPushButton('+', clicked=self.add_entry_price_quantity_row)
        self.entry_price_quantity_row_layout.addWidget(self.add_entry_price_quantity_slot)

        self.entry_price_quantity_layout.addWidget(self.entry_price_quantity_row_frame)

        self.exit_price_quantity_label = QLabel('Exit Price & Qty')

        self.exit_price_quantity_frame = QFrame()
        self.exit_price_quantity_layout = QVBoxLayout(self.exit_price_quantity_frame)

        self.exit_price_quantity_row_frame = QFrame()
        self.exit_price_quantity_row_layout = QHBoxLayout(self.exit_price_quantity_row_frame)

        self.exit_price_entry = QDoubleSpinBox()
        self.exit_price_entry.setRange(0, 1000000)
        self.exit_price_entry.setDecimals(2)
        self.exit_price_quantity_row_layout.addWidget(self.exit_price_entry)

        self.exit_quantity_entry = QSpinBox()
        self.exit_quantity_entry.setRange(1, 1000000)
        self.exit_price_quantity_row_layout.addWidget(self.exit_quantity_entry)

        self.add_exit_price_quantity_slot = QPushButton('+', clicked=self.add_exit_price_quantity_row)
        self.exit_price_quantity_row_layout.addWidget(self.add_exit_price_quantity_slot)
        self.exit_price_quantity_layout.addWidget(self.exit_price_quantity_row_frame)

        self.entry_time_label = QLabel('First entry time:')
        self.entry_time_entry = QDateTimeEdit()
        self.entry_time_entry.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.entry_time_entry.setCalendarPopup(True)

        self.exit_time_label = QLabel('Last exit time:')
        self.exit_time_entry = QDateTimeEdit()
        self.exit_time_entry.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.exit_time_entry.setCalendarPopup(True)

        self.profit_label = QLabel('Profit:')
        self.profit_entry = QDoubleSpinBox()
        self.profit_entry.setRange((-100000), 1000000)
        self.profit_entry.setDecimals(2)

        self.commission_label = QLabel('Commission:')
        self.commission_entry = QDoubleSpinBox()
        self.commission_entry.setRange(0, 1000000)
        self.commission_entry.setDecimals(2)

        self.left_side_layout.addWidget(self.instrument_label)
        self.left_side_layout.addWidget(self.instrument_entry)
        self.left_side_layout.addWidget(self.direction_label)
        self.left_side_layout.addWidget(self.direction_entry)
        self.left_side_layout.addWidget(self.entry_price_quantity_label)
        self.left_side_layout.addWidget(self.entry_price_quantity_frame)
        self.left_side_layout.addWidget(self.exit_price_quantity_label)
        self.left_side_layout.addWidget(self.exit_price_quantity_frame)
        self.left_side_layout.addWidget(self.entry_time_label)
        self.left_side_layout.addWidget(self.entry_time_entry)
        self.left_side_layout.addWidget(self.exit_time_label)
        self.left_side_layout.addWidget(self.exit_time_entry)
        self.left_side_layout.addWidget(self.profit_label)
        self.left_side_layout.addWidget(self.profit_entry)
        self.left_side_layout.addWidget(self.commission_label)
        self.left_side_layout.addWidget(self.commission_entry)

        self.screenshots_frame = QFrame()
        self.screenshots_layout = QVBoxLayout(self.screenshots_frame)

        self.htf_screenshot_label = QLabel('HTF SS:')
        self.htf_screenshot_row = ImageDropArea()

        self.itf_screenshot_label = QLabel('ITF SS:')
        self.itf_screenshot_row = ImageDropArea()

        self.ltf_screenshot_label = QLabel('LTF SS:')
        self.ltf_screenshot_row = ImageDropArea()

        self.screenshots_layout.addWidget(self.htf_screenshot_label)
        self.screenshots_layout.addWidget(self.htf_screenshot_row)
        self.screenshots_layout.addWidget(self.itf_screenshot_label)
        self.screenshots_layout.addWidget(self.itf_screenshot_row)
        self.screenshots_layout.addWidget(self.ltf_screenshot_label)
        self.screenshots_layout.addWidget(self.ltf_screenshot_row)

        self.strength_entry = QComboBox()
        self.strength_entry.addItem('Strength')
        self.strength_entry.addItems(['0', '1', '2'])
        self.strength_entry.setCurrentIndex(0)
        self.strength_entry.model().item(0).setEnabled(False)

        self.basetime_entry = QComboBox()
        self.basetime_entry.addItem('Base Time')
        self.basetime_entry.addItems(['0', '0.5', '1'])
        self.basetime_entry.setCurrentIndex(0)
        self.basetime_entry.model().item(0).setEnabled(False)

        self.freshness_entry = QComboBox()
        self.freshness_entry.addItem('Freshness')
        self.freshness_entry.addItems(['0', '1', '2'])
        self.freshness_entry.setCurrentIndex(0)
        self.freshness_entry.model().item(0).setEnabled(False)

        self.trend_entry = QComboBox()
        self.trend_entry.addItem('Trend')
        self.trend_entry.addItems(['0', '1', '2'])
        self.trend_entry.setCurrentIndex(0)
        self.trend_entry.model().item(0).setEnabled(False)

        self.curve_entry = QComboBox()
        self.curve_entry.addItem('Curve')
        self.curve_entry.addItems(['0', '0.5', '1'])
        self.curve_entry.setCurrentIndex(0)
        self.curve_entry.model().item(0).setEnabled(False)

        self.profit_zone_entry = QComboBox()
        self.profit_zone_entry.addItem('Profit Zone')
        self.profit_zone_entry.addItems(['0', '1', '2'])
        self.profit_zone_entry.setCurrentIndex(0)
        self.profit_zone_entry.model().item(0).setEnabled(False)

        self.right_side_frame = QFrame()
        self.right_side_layout = QVBoxLayout(self.right_side_frame)

        self.right_side_layout.addWidget(self.screenshots_frame)
        self.right_side_layout.addWidget(self.strength_entry)
        self.right_side_layout.addWidget(self.basetime_entry)
        self.right_side_layout.addWidget(self.freshness_entry)
        self.right_side_layout.addWidget(self.trend_entry)
        self.right_side_layout.addWidget(self.curve_entry)
        self.right_side_layout.addWidget(self.profit_zone_entry)

        self.create_trade_button = QPushButton('Create Trade', clicked=self.create_trade)
        self.clear_button = QPushButton('Clear All', clicked=self.clear_fields)

        self.right_side_layout.addWidget(self.clear_button)
        self.right_side_layout.addStretch()
        self.right_side_layout.addWidget(self.create_trade_button)

        self.layout.addWidget(self.left_side_frame)
        self.layout.addWidget(self.right_side_frame)

        self.set_current_datetime()
        self.setLayout(self.layout)

        self.entry_price_entries = [self.entry_price_entry]
        self.entry_quantity_entries = [self.entry_quantity_entry]
        self.exit_price_entries = [self.exit_price_entry]
        self.exit_quantity_entries = [self.exit_quantity_entry]

    def add_entry_price_quantity_row(self):
        try:
            entry_price_quantity_row_frame = QFrame()
            entry_price_quantity_row_layout = QHBoxLayout(entry_price_quantity_row_frame)

            entry_price_entry = QDoubleSpinBox()
            entry_price_entry.setRange(0, 1000000)
            entry_price_entry.setDecimals(2)
            entry_price_quantity_row_layout.addWidget(entry_price_entry)

            entry_quantity_entry = QSpinBox()
            entry_quantity_entry.setRange(1, 1000000)
            entry_price_quantity_row_layout.addWidget(entry_quantity_entry)

            delete_button = QPushButton('-')
            delete_button.clicked.connect(lambda: self.delete_entry_row(entry_price_quantity_row_frame, entry_price_entry, entry_quantity_entry))
            entry_price_quantity_row_layout.addWidget(delete_button)

            self.entry_price_quantity_layout.addWidget(entry_price_quantity_row_frame)

            self.entry_price_entries.append(entry_price_entry)
            self.entry_quantity_entries.append(entry_quantity_entry)

            self.adjust_window_size()
        except Exception as e:
            print(f'Failed to add entry price quantity row: {e}')

    def add_exit_price_quantity_row(self):
        try:
            exit_price_quantity_row_frame = QFrame()
            exit_price_quantity_row_layout = QHBoxLayout(exit_price_quantity_row_frame)

            exit_price_entry = QDoubleSpinBox()
            exit_price_entry.setRange(0, 1000000)
            exit_price_entry.setDecimals(2)
            exit_price_quantity_row_layout.addWidget(exit_price_entry)

            exit_quantity_entry = QSpinBox()
            exit_quantity_entry.setRange(1, 1000000)
            exit_price_quantity_row_layout.addWidget(exit_quantity_entry)

            delete_button = QPushButton('-')
            delete_button.clicked.connect(lambda: self.delete_exit_row(exit_price_quantity_row_frame, exit_price_entry, exit_quantity_entry))
            exit_price_quantity_row_layout.addWidget(delete_button)

            self.exit_price_quantity_layout.addWidget(exit_price_quantity_row_frame)

            self.exit_price_entries.append(exit_price_entry)
            self.exit_quantity_entries.append(exit_quantity_entry)

            self.adjust_window_size()
        except Exception as e:
            print(f'Failed to add exit price quantity row: {e}')

    def delete_entry_row(self, row_frame, entry_price_entry, entry_quantity_entry):
        try:
            self.entry_price_quantity_layout.removeWidget(row_frame)
            row_frame.deleteLater()
            self.entry_price_entries.remove(entry_price_entry)
            self.entry_quantity_entries.remove(entry_quantity_entry)
            self.adjust_window_size()
        except Exception as e:
            print(f'Failed to delete entry price quantity row: {e}')

    def delete_exit_row(self, row_frame, exit_price_entry, exit_quantity_entry):
        try:
            self.exit_price_quantity_layout.removeWidget(row_frame)
            row_frame.deleteLater()
            self.exit_price_entries.remove(exit_price_entry)
            self.exit_quantity_entries.remove(exit_quantity_entry)
            self.adjust_window_size()
        except Exception as e:
            print(f'Failed to delete exit price quantity row: {e}')

    def create_trade(self):
        try:
            instrument = self.instrument_entry.text()
            direction = self.direction_entry.currentText()

            entries = []
            for price_entry, quantity_entry in zip(self.entry_price_entries, self.entry_quantity_entries):
                entry_price = price_entry.value()
                entry_quantity = quantity_entry.value()
                entries.append((entry_price, entry_quantity))

            exits = []
            for price_entry, quantity_entry in zip(self.exit_price_entries, self.exit_quantity_entries):
                exit_price = price_entry.value()
                exit_quantity = quantity_entry.value()
                exits.append((exit_price, exit_quantity))

            entry_time = self.entry_time_entry.dateTime().toString('yyyy-MM-dd HH:mm:ss')
            exit_time = self.exit_time_entry.dateTime().toString('yyyy-MM-dd HH:mm:ss')
            profit = self.profit_entry.value()
            commission = self.commission_entry.value()
            strength = int(self.strength_entry.currentText())
            basetime = float(self.basetime_entry.currentText())
            freshness = int(self.freshness_entry.currentText())
            trend = int(self.trend_entry.currentText())
            curve = float(self.curve_entry.currentText())
            profit_zone = int(self.profit_zone_entry.currentText())

            # Check if all fields are filled out
            if not all([instrument, direction, entries, exits, entry_time, exit_time, profit]):
                print(f"All fields must be filled out. {instrument}, {direction}, {entries}, {exits}, {entry_time}, {exit_time}, {profit}, {commission}, {strength}, {basetime}, {freshness}, {trend}, {curve}, {profit_zone}")
                return

            screenshots = []
            for label, screenshot_row in zip(['HTF', 'ITF', 'LTF'], [self.htf_screenshot_row, self.itf_screenshot_row, self.ltf_screenshot_row]):
                screenshot_name = screenshot_row.line_edit.text()
                if screenshot_name != "Drop an image here":
                    screenshot_row.get_file_path()
                    screenshot_path = screenshot_row.get_file_path()
                    try:
                        with open(screenshot_path, 'rb') as file:
                            screenshot_data = file.read()
                            screenshots.append((label, screenshot_data))
                    except Exception as e:
                        print(f"Failed to read screenshot {screenshot_name}: {e}")
                        return
            account_id = self.account_id
            trade_data = {
                "account_id": account_id,
                "instrument": instrument,
                "direction": direction,
                "entries": entries,
                "exits": exits,
                "entry_time": entry_time,
                "exit_time": exit_time,
                "profit": profit,
                "commission": commission,
                "strength": strength,
                "basetime": basetime,
                "freshness": freshness,
                "trend": trend,
                "curve": curve,
                "profitzone": profit_zone
            }

            if save_trade_with_screenshots(trade_data, screenshots):
                print("Trade inserted successfully.")
                self.trade_created.emit(account_id)
                self.close()
            else:
                print("Failed to insert trade.")
        except Exception as e:
            print(f'Failed to send trade database: {e}')


    def clear_fields(self):
        self.instrument_entry.clear()
        self.direction_entry.setCurrentIndex(0)
        self.entry_price_entries = [self.entry_price_entry]
        self.entry_quantity_entries = [self.entry_quantity_entry]
        self.exit_price_entries = [self.exit_price_entry]
        self.exit_quantity_entries = [self.exit_quantity_entry]
        self.entry_price_quantity_layout.addWidget(self.entry_price_quantity_row_frame)
        self.exit_price_quantity_layout.addWidget(self.exit_price_quantity_row_frame)
        self.set_current_datetime()
        self.profit_entry.setValue(0)
        self.commission_entry.setValue(0)
        self.strength_entry.setCurrentIndex(0)
        self.basetime_entry.setCurrentIndex(0)
        self.freshness_entry.setCurrentIndex(0)
        self.trend_entry.setCurrentIndex(0)
        self.curve_entry.setCurrentIndex(0)
        self.profit_zone_entry.setCurrentIndex(0)
        self.adjust_window_size()

    def set_current_datetime(self):
        current_datetime = QDateTime.currentDateTime()
        self.entry_time_entry.setDateTime(current_datetime)
        self.exit_time_entry.setDateTime(current_datetime)

    def adjust_window_size(self):
        self.adjustSize()

    def resizeEvent(self, event):
        self.adjustSize()
        super().resizeEvent(event)

class NTNewTradePopup(QWidget):
    trade_created = pyqtSignal(int)

    def __init__(self, parent=None, width=None, height=None):
        super().__init__(parent)
        self.user_id = UserSession().get_user_id()
        self.account_id = None
        self.account_name = None

        if width:
            self.setMaximumWidth(width)
        if height:
            self.setMaximumHeight(height)

        self.setupUI()
        self.setStyleSheet("""
        QWidget {
            background-color: #222222;
            color: white;
        }""")

    def setupUI(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        self.stack = QStackedWidget(frame)
        layout.addWidget(self.stack)

        self.button_frame = QFrame()
        self.button_layout = QVBoxLayout(self.button_frame)
        self.button_frame.setLayout(self.button_layout)

        self.new_trades_button = QPushButton('Add Trade(s)', clicked=self.open_file_dialog)
        self.new_trades_button.setStyleSheet("""
                    QPushButton:hover {
                        background-color: #2c7e33;
                    }""")

        self.button_layout.addWidget(self.new_trades_button)

        self.multiple_info_frame = QFrame()
        self.multiple_info_layout = QHBoxLayout(self.multiple_info_frame)

        self.stack.addWidget(self.button_frame)
        self.stack.setCurrentWidget(self.button_frame)

        self.setLayout(layout)

    def open_file_dialog(self):
        # Options for the file dialog
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV file from NinjaTrader.", "",
                                                   "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                self.check_for_new_trades(file_name)
            except Exception as e:
                print(f"Error processing file: {e}")

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
            print(f"No trades found for account '{self.account_name}' in the CSV file.")
            return

        grouped_trades = group_trades_by_entry_time(new_trades)

        existing_trades = get_trades_for_account(self.account_id)
        if existing_trades:
            # Convert existing trades to a DataFrame for easy comparison
            existing_trades_df = pd.DataFrame(existing_trades)

            # Compare entry times to find new trades
            last_entry_time = existing_trades_df['entry_time'].max()
            new_trades_to_insert = grouped_trades[grouped_trades['entry_time'] > last_entry_time]

            if new_trades_to_insert.empty:
                print("No new trades to update.")
                print(existing_trades)
            else:
                print(f"Found {len(new_trades_to_insert)} new trade(s) to insert.")
                self.save_new_trades_to_db(new_trades_to_insert)
                self.trade_created.emit(self.account_id)

        else:
            print('No existing trades found. Saving all trades as new trades.')
            self.save_new_trades_to_db(grouped_trades)
            self.trade_created.emit(self.account_id)


    def adjust_window_size(self):
        self.adjustSize()

    def resizeEvent(self, event):
        self.adjustSize()
        super().resizeEvent(event)

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
            'exit_time': 'last',         # Take the last exit time
            'instrument': 'first',       # Assuming all rows have the same instrument, take the first
            'direction': 'first',        # Assuming direction is the same, take the first
            'entry_price': lambda x: (x * data.loc[x.index, 'quantity']).sum() / data.loc[x.index, 'quantity'].sum(),  # Weighted average entry price
            'exit_price': lambda x: (x * data.loc[x.index, 'quantity']).sum() / data.loc[x.index, 'quantity'].sum(),   # Weighted average exit price
            'quantity': 'sum',           # Sum up the quantities
            'profit': 'sum',             # Sum up the profit
            'com': 'sum'                 # Sum up the commissions
        }
    ).reset_index()

    return grouped_data
