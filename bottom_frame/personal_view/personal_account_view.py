import os
import sys

import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mplcursors
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QDate, QPropertyAnimation, pyqtSignal
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta

# Custom imports (assuming these are custom modules)
from SQL import get_trades_for_account, UserSession, check_account_money_visibility, update_money_visibility
from bottom_frame.personal_view.new_trade_popups import ManualNewTradePopup
from bottom_frame.personal_view.trade_info import TradeInfoInputView
from bottom_frame.custom_widgets import CustomNoteView, FiledropFrame, CustomCalendar


def load_icon(file_name):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(resource_path(f"resources/{file_name}")),
                   QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return icon


class PersonalAccountsView(QWidget):
    disable_account_list_signal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icons = {
            "view": load_icon("view.png"),
            "hide": load_icon("hide.png"),
            "add_trade": load_icon("add_trade.png"),
            "cancel_trade": load_icon("cancel_trade_update.png")
        }
        self.user_id = UserSession().get_user_id()
        self.daily_note_view = None
        self.ninjatrader_update_button = None
        self.manual_add_trade_button = None
        self.trade_info_input_view = None
        self.first_dateEdit = None
        self.second_dateEdit = None
        self.dateedit_start_date = None
        self.dateedit_end_date = None
        self.first_date = None
        self.second_date = None
        self.bar_first_date = None
        self.bar_second_date = None
        self.current_account = None
        self.correct_label = None
        self.current_date = QDate.currentDate()
        self.account_type = None
        self.account_data = None
        self.account_id = None
        self.filtered_data = None
        self.new_trade_popup = None
        self.updating_trades = False
        self.money_visible = True
        self.user_id = UserSession().get_user_id()

        self.setup_ui()
        self.setLayout(self.main_layout)

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_top_frame()
        self.setup_bottom_frame()

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
        self.top_frame_title = QLabel("Select a Account.")
        self.top_frame_title.setStyleSheet("""            
        QWidget {
            color: white;
        }""")
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.top_frame_title.setFont(font)
        self.top_frame_title.setAlignment(Qt.AlignCenter)

    def setup_bottom_frame(self):
        self.bottom_frame = QFrame()
        self.bottom_frame_layout = QVBoxLayout(self.bottom_frame)
        self.bottom_frame_layout.setSpacing(0)
        self.bottom_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_frame = self.createStatsFrame()
        self.graphs_frame = self.createGraphsFrame()
        self.bottom_frame_layout.addWidget(self.stats_frame)
        self.bottom_frame_layout.addWidget(self.graphs_frame)
        self.main_layout.addWidget(self.bottom_frame)
        self.stats_frame.setStyleSheet("color: white;")

    def createStatsFrame(self):
        stats_frame = QFrame(self.bottom_frame)
        stats_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        stats_frame_layout_horizontal = QHBoxLayout(stats_frame)
        (self.main_stats_frame,
         self.first_stats_label,
         self.second_stats_label,
         self.third_stats_label,
         self.add_new_trade_button,
         self.cancel_trade_update_button,
         self.confirm_trade_update_button,
         self.money_visibility_button,
         self.second_stats_frame) = self.createStatsBox()
        stats_frame_layout_horizontal.addWidget(self.main_stats_frame)
        stats_frame_layout_horizontal.setStretch(0, 1)
        stats_frame_layout_horizontal.setStretch(1, 1)
        return stats_frame

    def createStatsBox(self):
        frame = QFrame()
        stats_layout = QHBoxLayout(frame)
        frame.setStyleSheet("""
            border: 2px solid #c3dc9b;
            border-radius: 5px;
            background-color: #333333;
        """)

        first_stats_frame = QFrame()
        first_stats_frame.setStyleSheet("border:none;")
        first_stats_layout = QHBoxLayout(first_stats_frame)
        first_stats_label = QLabel()
        first_stats_vis_button = QPushButton(self, clicked=self.visibility_button_pressed)
        first_stats_layout.addWidget(first_stats_vis_button, alignment=Qt.AlignLeft)
        first_stats_vis_button.setIcon(self.icons["hide"])
        first_stats_label.setStyleSheet("border:none;")
        first_stats_label.setAlignment(Qt.AlignRight)
        first_stats_layout.addWidget(first_stats_label)

        second_stats_frame = FiledropFrame()
        second_stats_layout = QHBoxLayout(second_stats_frame)

        cancel_update_button = QPushButton()
        cancel_update_button.setStyleSheet('border:none;')
        cancel_update_button.setIcon(self.icons["cancel_trade"])

        confirm_update_button = QPushButton()
        confirm_update_button.setStyleSheet('border:none;')
        confirm_update_button.setIcon(self.icons["add_trade"])
        second_stats_label = QLabel()
        second_stats_label.setText('Information will be displayed here.')
        second_stats_label.setStyleSheet("border:none; background-color: #222222;")
        second_stats_label.setAlignment(Qt.AlignCenter)
        second_stats_layout.addWidget(cancel_update_button, alignment=Qt.AlignLeft)
        second_stats_layout.addWidget(second_stats_label)
        second_stats_layout.addWidget(confirm_update_button, alignment=Qt.AlignRight)
        cancel_update_button.setVisible(False)
        confirm_update_button.setVisible(False)
        second_stats_frame.cancel_button = cancel_update_button
        second_stats_frame.confirm_button = confirm_update_button
        second_stats_frame.label = second_stats_label

        third_stats_frame = QFrame()
        third_stats_frame.setStyleSheet("border:none; ")

        third_stats_layout = QHBoxLayout(third_stats_frame)

        third_stats_label = QLabel()
        third_stats_label.setStyleSheet("border:none;")
        third_stats_label.setAlignment(Qt.AlignLeft)

        edit_button = QPushButton('', clicked=self.new_trade_button_pressed)
        edit_button.setIcon(self.icons["add_trade"])
        third_stats_layout.addWidget(third_stats_label)
        third_stats_layout.addWidget(edit_button, alignment=Qt.AlignRight)

        stats_layout.addWidget(first_stats_frame)
        stats_layout.addWidget(second_stats_frame)
        stats_layout.addWidget(third_stats_frame)

        return (frame, first_stats_label, second_stats_label, third_stats_label, edit_button,
                cancel_update_button, confirm_update_button, first_stats_vis_button, second_stats_frame)

    def new_trade_button_pressed(self):
        try:
            if self.current_account:
                if self.account_type == 'NinjaTrader':
                    if self.updating_trades:
                        self.new_trade_button_changes_second_stats(visible=False)
                        self.second_stats_frame.setAcceptDrops(False)
                        self.add_new_trade_button.setIcon(self.icons["add_trade"])
                    else:
                        self.new_trade_button_changes_second_stats(visible=True)
                        self.second_stats_frame.setAcceptDrops(True)
                        self.second_stats_frame.trade_created.connect(self.fetch_account_data)
                        self.add_new_trade_button.setIcon(self.icons["cancel_trade"])
                elif self.account_type == 'Manual' or self.account_type == 'Backtest':
                    if not self.new_trade_popup:
                        height = int(self.second_graph_stack.height())
                        width = int(self.second_graph_stack.width())
                        self.new_trade_popup = ManualNewTradePopup(self, height=height, width=width)
                        self.new_trade_popup.trade_created.connect(self.fetch_account_data)

                        self.new_trade_popup.account_id = self.account_id
                        self.new_trade_popup.account_name = self.current_account
                        self.animate_new_trade_popup(show=True)
                    else:
                        self.animate_new_trade_popup(show=False)
            else:
                print('No account selected.')
                return
        except Exception as e:
            print(f'Failed to toggle nt new trade: {e}')

    def center_new_trade_popup(self):
        stack_pos = self.second_graph_stack.mapToGlobal(self.second_graph_stack.rect().center())
        popup_x = int(stack_pos.x() - self.new_trade_popup.width() / 2)
        popup_y = int(stack_pos.y() - self.new_trade_popup.height() / 2)
        self.new_trade_popup.move(popup_x, popup_y)

    def visibility_button_pressed(self):
        if self.current_account:
            if self.money_visible:
                self.money_visible = False
                self.money_visibility_button.setIcon(self.icons["view"])
                update_money_visibility(self.account_id, self.money_visible)
                self.fetch_account_data(self.account_id, visibility_button=True)
                print('Trades are currently visible setting to invisible.')
            else:
                self.money_visible = True
                self.money_visibility_button.setIcon(self.icons["hide"])
                update_money_visibility(self.account_id, self.money_visible)
                self.fetch_account_data(self.account_id, visibility_button=True)
                print('Trades are currently invisible setting to visible.')
        else:
            print('No account selected.')

    def new_trade_button_changes_second_stats(self, visible=False):
        if visible:
            self.updating_trades = True
            self.second_stats_label.setText('Drag csv file here to update trades.\n'
                                            '(Click to browse computer files.)')
        else:
            self.updating_trades = False
            self.cancel_trade_update_button.setVisible(False)
            self.confirm_trade_update_button.setVisible(False)
            if self.correct_label:
                self.second_stats_label.setText(self.correct_label)

    def createGraphsFrame(self):
        graphs_frame = QFrame(self.bottom_frame)
        graphs_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        horizontal_layout = QHBoxLayout(graphs_frame)

        self.first_graph_stack = QStackedWidget(graphs_frame)
        self.second_graph_stack = QStackedWidget(graphs_frame)
        self.third_graph_stack = QStackedWidget(graphs_frame)
        for stack in (self.first_graph_stack, self.second_graph_stack, self.third_graph_stack):
            stack.setStyleSheet("""
            QStackedWidget {
                border: 2px solid #c3dc9b;
                border-radius: 5px;
                background-color: #222222;
            }
        """)

        self.first_graph_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.second_graph_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.third_graph_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.first_graph_stack.setMinimumWidth(int(graphs_frame.width() / 3))
        self.second_graph_stack.setMinimumWidth(int(graphs_frame.width() / 3))
        self.third_graph_stack.setMinimumWidth(int(graphs_frame.width() / 3))

        horizontal_layout.addWidget(self.first_graph_stack)
        horizontal_layout.addWidget(self.second_graph_stack)
        horizontal_layout.addWidget(self.third_graph_stack)
        horizontal_layout.setStretch(0, 1)
        horizontal_layout.setStretch(1, 1)
        horizontal_layout.setStretch(2, 1)
        return graphs_frame

    def get_current_week_date_range(self):
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
        end_of_week = start_of_week + timedelta(days=6)  # Sunday of the current week
        return start_of_week, end_of_week

    def fetch_account_data(self, account_id, visibility_button=False):
        try:
            trades = get_trades_for_account(account_id)
            self.second_stats_frame.account_name = self.current_account
            self.second_stats_frame.account_id = self.account_id
            self.money_visible = check_account_money_visibility(self.account_id)
            if self.money_visible:
                self.money_visibility_button.setIcon(self.icons['hide'])
            else:
                self.money_visibility_button.setIcon(self.icons['view'])
            if trades:
                self.account_data = trades_to_dataframe(trades)
                if visibility_button:
                    if self.dateedit_start_date and self.dateedit_end_date:
                        start_date, end_date = self.dateedit_start_date, self.dateedit_end_date
                        filtered_data = self.filter_data_by_date_range(self.account_data, self.dateedit_start_date,
                                                                       self.dateedit_end_date)
                    else:
                        start_date, end_date = self.get_current_week_date_range()
                        filtered_data = self.filter_data_by_date_range(self.account_data, start_date.strftime('%Y-%m-%d'),
                                                                       end_date.strftime('%Y-%m-%d'))
                else:
                    start_date, end_date = self.get_current_week_date_range()
                    filtered_data = self.filter_data_by_date_range(self.account_data, start_date.strftime('%Y-%m-%d'),
                                                                   end_date.strftime('%Y-%m-%d'))
                self.filtered_data = filtered_data
                self.updateStatsLabels(filtered_data)
                self.plot_line_graph(filtered_data)
                self.plot_trade_performance(filtered_data)
                self.plot_calendar(filtered_data)
                self.updateDateEdit(start_date=start_date, end_date=end_date)
                print(f"Fetching data for account: {account_id}")
                self.first_dateEdit.setEnabled(True)
                self.second_dateEdit.setEnabled(True)
            else:
                print('No trades available.')
                self.second_stats_label.setText('No trades.')
                blank_widgets = [QWidget() for _ in range(3)]
                stacks = [self.first_graph_stack, self.second_graph_stack, self.third_graph_stack]

                for stack, blank_widget in zip(stacks, blank_widgets):
                    stack.addWidget(blank_widget)
                    stack.setCurrentWidget(blank_widget)

        except Exception as e:
            print(f'Failed to fetch account data: {e}')

    def updateWhenDateChanged(self):
        start_date = self.first_dateEdit.date().toString("yyyy-MM-dd")
        end_date = self.second_dateEdit.date().toString("yyyy-MM-dd")
        self.dateedit_start_date = start_date
        self.dateedit_end_date = end_date
        filtered_data = self.filter_data_by_date_range(self.account_data, start_date, end_date)
        self.filtered_data = filtered_data
        self.updateStatsLabels(filtered_data)
        self.plot_line_graph(filtered_data)
        self.plot_trade_performance(filtered_data)
        self.plot_calendar(filtered_data)
        self.updateDateEdit(start_date=start_date, end_date=end_date)
        self.new_trade_button_changes_second_stats(visible=False)
        print('Updated when changed date edit.')

    def updateWhenDayClicked(self, day=None, first_date=None, second_date=None):
        start_date = day if day else first_date
        end_date = day if day else second_date
        filtered_data = self.filter_data_by_date_range(self.account_data, start_date, end_date)
        self.filtered_data = filtered_data
        self.updateStatsLabels(filtered_data)
        self.plot_line_graph(filtered_data)
        self.plot_trade_performance(filtered_data)
        if not day:
            self.plot_calendar(filtered_data)
        print('Updated when changed date edit.')

    def updateDateEdit(self, start_date=None, end_date=None):
        self.first_dateEdit.setEnabled(False)
        self.second_dateEdit.setEnabled(False)

        self.first_dateEdit.clearMaximumDate()
        self.first_dateEdit.clearMinimumDate()
        self.second_dateEdit.clearMaximumDate()
        self.second_dateEdit.clearMinimumDate()
        self.first_dateEdit.blockSignals(True)
        self.second_dateEdit.blockSignals(True)

        account_first_date = pd.to_datetime(self.account_data['entry_time']).min()
        account_last_date = pd.to_datetime(self.account_data['exit_time']).max()
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        if not start_date and not end_date:
            start_date, end_date = self.get_current_week_date_range()
            print('setting to weekly.')
        print(f'setting to choosen dates: {start_date} and {end_date}')

        if pd.isnull(account_first_date) or pd.isnull(account_last_date):
            print("Invalid date range")
            return

        self.first_dateEdit.setDate(QDate(start_date.year, start_date.month, start_date.day))
        self.second_dateEdit.setDate(QDate(end_date.year, end_date.month, end_date.day))

        self.first_dateEdit.setMinimumDate(
            QDate(account_first_date.year, account_first_date.month, account_first_date.day))
        self.first_dateEdit.setMaximumDate(
            QDate(account_last_date.year, account_last_date.month, account_last_date.day))
        self.second_dateEdit.setMinimumDate(
            QDate(account_first_date.year, account_first_date.month, account_first_date.day))
        self.second_dateEdit.setMaximumDate(
            QDate(account_last_date.year, account_last_date.month, account_last_date.day))
        self.first_dateEdit.blockSignals(False)
        self.second_dateEdit.blockSignals(False)
        self.first_dateEdit.setEnabled(True)
        self.second_dateEdit.setEnabled(True)

    def filter_data_by_date_range(self, data, start_date, end_date):
        data = data.copy()
        data['exit_time'] = pd.to_datetime(data['exit_time'], format="%Y-%m-%d %H:%M:%S")
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        data = data[(data['exit_time'] >= start_date) & (data['exit_time'] <= end_date)]
        data['exit_time'] = data['exit_time'].dt.strftime("%Y-%m-%d %H:%M:%S")
        return data

    def updateStatsLabels(self, data):
        grouped_data = data.groupby('entry_time').agg(
            {'profit': 'sum', 'direction': 'first', 'instrument': 'first'}).reset_index()

        w_be_l = grouped_data.apply(
            lambda row: 'L' if row['profit'] < 0 else ('B' if row['profit'] == 0
                                                       else 'W'), axis=1)
        grouped_data['result'] = w_be_l
        net_pnl = grouped_data['profit'].sum()
        total_trades = len(grouped_data['result'])
        self.total_trades = total_trades
        winning_trades = len(grouped_data[grouped_data['result'] == 'W'])
        losing_trades = len(grouped_data[grouped_data['result'] == 'L'])
        break_even_trades = len(grouped_data[grouped_data['result'] == 'B'])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        loss_rate = (losing_trades / total_trades) * 100 if total_trades > 0 else 0
        break_even_rate = (break_even_trades / total_trades) * 100 if total_trades > 0 else 0
        avg_win = grouped_data[grouped_data['result'] == 'W']['profit'].mean()
        avg_loss = grouped_data[grouped_data['result'] == 'L']['profit'].mean()
        avg_rr = avg_win / np.abs(avg_loss)
        np_color = '#c3dc9b' if net_pnl > 0 else '#ff7f7f'

        avg_win = f'{avg_win:.2f}' if self.money_visible else '---'
        avg_loss = f'{avg_loss:.2f}' if self.money_visible else '---'
        net_pnl = f'{net_pnl:.2f}' if self.money_visible else '---'
        self.first_stats_label.setText(f'<span style="color:#c3dc9b;">Avg Win: </span>'
                                       f'<span style="color:white;">${avg_win}</span><br>'
                                       f'<span style="color:#ff7f7f;">Avg Loss: </span>'
                                       f'<span style="color:white;">${avg_loss}</span><br>'
                                       f'<span style="color:#f4e66e;">Avg RR ratio: </span>'
                                       f'<span style="color:white;">{avg_rr:.2f}</span>')
        self.second_stats_label.setText(f'<span style="color:white;">Number of Trades: </span>'
                                        f'<span style="color:#c3dc9b;"> {total_trades}</span><br>'
                                        f'<span style="color:white;">Net Profit: </span>'
                                        f'<span style="color:{np_color};"> {net_pnl} </span>')
        self.correct_label = self.second_stats_label.text()
        self.third_stats_label.setText(f'<span style="color:#c3dc9b;">Win Rate: </span>'
                                       f'<span style="color:white;">{win_rate:.2f}%</span><br>'
                                       f'<span style="color:#ff7f7f;">Loss Rate: </span>'
                                       f'<span style="color:white;">{loss_rate:.2f}%</span><br>'
                                       f'<span style="color:#f4e66e;">B/e Rate: </span>'
                                       f'<span style="color:white;">{break_even_rate:.2f}%</span>')

    def plot_line_graph(self, data):
        try:
            self.first_graph_stack.setCurrentIndex(-1)

            filtered_data = data.copy()
            filtered_data.loc[:, 'entry_time'] = pd.to_datetime(data['entry_time'])
            if filtered_data.empty:
                label = QLabel("No trades were made in this date range.")
                self.first_graph_stack.addWidget(label)
                self.first_graph_stack.setCurrentWidget(label)
                return

            cumulative_progress = filtered_data.groupby('entry_time')['profit'].sum().cumsum()
            fig, ax = plt.subplots(constrained_layout=True)
            fig.patch.set_facecolor('#222222')
            ax.set_facecolor('#222222')
            line, = ax.plot(cumulative_progress.index, cumulative_progress, color='white', label='Cumulative Profit',
                            linewidth=1)
            positive_profits = filtered_data[filtered_data['profit'] > 0]
            negative_profits = filtered_data[filtered_data['profit'] <= 0]

            ax.scatter(positive_profits['entry_time'], cumulative_progress[positive_profits['entry_time']],
                       color='#c3dc9b', s=25, zorder=5, label='Positive Trades')

            ax.scatter(negative_profits['entry_time'], cumulative_progress[negative_profits['entry_time']],
                       color='#ff4c4c', s=25, zorder=5, label='Negative Trades')
            ax.grid(False)
            ax.axhline(0, color='white', linestyle='--', linewidth=0.7, label='$0')
            for spine in ax.spines.values():
                spine.set_edgecolor('#c3dc9b')
            cursor = mplcursors.cursor(line, hover=True)
            cursor.connect("add", lambda sel: self.show_annotation(sel, cumulative_progress=cumulative_progress))
            fig.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
            ax.set_title('P&L Chart', color='white')
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.legend()
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("border: 2px solid #c3dc9b;")
            self.first_graph_stack.addWidget(canvas)
            self.first_graph_stack.setCurrentWidget(canvas)
            plt.close(fig)
        except Exception as e:
            print(f"Error plotting graph: {e}")

    def plot_trade_performance(self, data):
        try:
            self.second_graph_stack.setCurrentIndex(-1)

            filtered_data = data.copy()
            filtered_data.loc[:, 'entry_time'] = pd.to_datetime(filtered_data['entry_time'], errors='coerce')
            if filtered_data.empty:
                label = QLabel("No trades were made in this date range.")
                self.second_graph_stack.addWidget(label)
                self.second_graph_stack.setCurrentWidget(label)
                return

            grouped_data = filtered_data.groupby('entry_time').agg(profit=('profit', 'sum'),
                                                                   direction=('direction', 'first'),
                                                                   instrument=('instrument', 'first'),
                                                                   exit_time=('exit_time', 'last'),
                                                                   trade_id=('trade_id', 'first')).reset_index()
            min_bar_height = 15
            toggle_values = [min_bar_height, -min_bar_height]

            # Create a variable to keep track of the current index
            toggle_index = [0]  # Using a list to allow modification within the lambda

            def adjust_profit(x):
                if x == 0:
                    value = toggle_values[toggle_index[0] % 2]
                    toggle_index[0] += 1
                    return value
                else:
                    return x

            grouped_data['adjusted_profit'] = grouped_data['profit'].apply(adjust_profit)

            fig, ax = plt.subplots(constrained_layout=True)
            fig.patch.set_facecolor('#222222')
            ax.set_facecolor('#222222')

            bar_colors = np.where(grouped_data['profit'] > 0, '#c3dc9b',
                                  np.where(grouped_data['profit'] < 0, '#ff7f7f', 'white'))

            bars = ax.bar(grouped_data.index + 1, grouped_data['adjusted_profit'],
                          color=bar_colors)

            ax.axhline(0, color='white', linewidth=0.8)
            for spine in ax.spines.values():
                spine.set_edgecolor('#c3dc9b')

            ax.set_title('Trade Performance', color='white')
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_xticks(range(1, len(grouped_data) + 1))

            # Cursor and click events
            cursor = mplcursors.cursor(bars, hover=True)
            cursor.connect("add", lambda sel: self.show_annotation(sel, grouped_data=grouped_data))
            fig.canvas.mpl_connect('button_press_event', lambda event: self.on_bar_clicked(event, bars, grouped_data))
            fig.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

            # Add the plot to the stack
            canvas = FigureCanvas(fig)
            self.second_graph_stack.addWidget(canvas)
            self.second_graph_stack.setCurrentWidget(canvas)
            plt.close(fig)
        except Exception as e:
            print(f"Error plotting trade performance: {e}")

    def plot_calendar(self, data):
        try:
            self.third_graph_stack.setCurrentIndex(-1)

            self.calendar = CustomCalendar(parent=None, account_type='Manual', money_visible=self.money_visible)
            self.first_dateEdit = self.calendar.fde
            self.first_dateEdit.dateChanged.connect(self.updateWhenDateChanged)
            self.second_dateEdit = self.calendar.sde
            self.second_dateEdit.dateChanged.connect(self.updateWhenDateChanged)
            self.calendar.day_clicked.connect(self.third_stack_day_clicked)
            self.calendar.account_id = self.account_id
            self.calendar.account_data = data
            self.calendar.update_calendar(data)
            self.third_graph_stack.addWidget(self.calendar)
            self.third_graph_stack.setCurrentWidget(self.calendar)
            self.show()
        except Exception as e:
            print(f"Error plotting calendar: {e}")

    def on_bar_clicked(self, event, bars, data):
        try:
            bar_contains = [bar.contains(event)[0] for bar in bars]
            if any(bar_contains):
                bar_index = bar_contains.index(True)
                trade_info = data.iloc[bar_index].copy()
                if isinstance(trade_info['entry_time'], str):
                    trade_info.loc['entry_time'] = pd.to_datetime(trade_info['entry_time'], errors='coerce')
                if isinstance(trade_info['exit_time'], str):
                    trade_info.loc['exit_time'] = pd.to_datetime(trade_info['exit_time'], errors='coerce')
                if self.daily_note_view:
                    self.bar_first_date, self.bar_second_date = str(trade_info.loc['exit_time']), str(
                        trade_info.loc['exit_time'])
                else:
                    self.bar_first_date, self.bar_second_date = self.first_dateEdit.date().toString(
                        "yyyy-MM-dd"), self.second_dateEdit.date().toString("yyyy-MM-dd")
                self.reload_stacks(show='Info', data=trade_info)
            else:
                print('No bar was clicked.')
        except Exception as e:
            print(f'On click bar function failed: {e}')

    def on_mouse_move(self, event):
        if not event.inaxes:
            if hasattr(self, 'active_annotation') and self.active_annotation:
                self.active_annotation.set_visible(False)
                event.canvas.draw_idle()

    def show_annotation(self, sel, cumulative_progress=None, grouped_data=None):
        try:
            if cumulative_progress is not None:
                profit = f'{cumulative_progress.iloc[int(sel.index)]:.2f}'
                formatted_profit = profit if self.money_visible else '---'
            if grouped_data is not None:
                profit = f'{grouped_data['profit'].iloc[sel.index]:.2f}'
                formatted_profit = profit if self.money_visible else '---'
            sel.annotation.set_text(
                f"Date: {cumulative_progress.index[int(sel.index)].strftime('%m/%d - %H:%M')}\n"
                f"Profit: {formatted_profit}"
                if cumulative_progress is not None else
                f"Date: {grouped_data['entry_time'].iloc[sel.index].strftime('%Y-%m-%d %H:%M')}\n"
                f"Profit: ${formatted_profit}\n"
                f"Instrument: {grouped_data['instrument'].iloc[sel.index]}"
            )
            sel.annotation.get_bbox_patch().set(fc='black', alpha=0.6)
            sel.annotation.get_bbox_patch().set_edgecolor('none')
            sel.annotation.set_color('white')
            sel.annotation.set_visible(True)

            if isinstance(sel.artist, plt.Line2D):
                sel.artist.figure.canvas.draw_idle()
            elif isinstance(sel.artist, plt.Rectangle):
                sel.artist.figure.canvas.draw_idle()

            self.active_annotation = sel.annotation
        except Exception as e:
            print(f'Failed to generate annotation: {e}')

    def reload_stacks(self, show=None, data=None):
        try:
            if show == 'Info' and data is not None:
                trade_id = int(data['trade_id'])
                # Clicking a bar changes the first, second, and third stack.
                self.add_new_trade_button.setVisible(False)
                self.new_trade_button_changes_second_stats(visible=False)
                self.second_changes_third_to_notes(trade_id)
                self.second_changes_first_to_screenshot()
                # Create Trade info view
                self.trade_info_input_view = TradeInfoInputView(data=data, note_view=self.trade_note_view)
                # Label and connect screenshot areas to change first graph.
                screenshot_areas = [self.trade_info_input_view.screenshot_areas['HTF'],
                                    self.trade_info_input_view.screenshot_areas['ITF'],
                                    self.trade_info_input_view.screenshot_areas['LTF']]
                for screenshot_area in screenshot_areas:
                    screenshot_area.screenshot_clicked.connect(self.second_changes_first_to_screenshot)

                self.trade_info_input_view.go_back_button.clicked.connect(self.second_stack_go_back_pressed)

                self.second_graph_stack.addWidget(self.trade_info_input_view)
                self.second_graph_stack.setCurrentWidget(self.trade_info_input_view)
            if show == 'bar_graph' and data is None:
                self.add_new_trade_button.setVisible(True)
                if self.filtered_data is not None:
                    if self.bar_first_date != self.bar_second_date:
                        self.plot_trade_performance(self.filtered_data)
                        self.plot_line_graph(self.filtered_data)
                        self.plot_calendar(self.filtered_data)
                        self.updateDateEdit(start_date=self.bar_first_date, end_date=self.bar_second_date)
                    else:
                        self.plot_trade_performance(self.filtered_data)
                        self.plot_line_graph(self.filtered_data)
                        if self.daily_note_view:
                            self.third_graph_stack.setCurrentWidget(self.daily_note_view)
                        else:
                            self.plot_calendar(self.filtered_data)
                            self.add_new_trade_button.setVisible(True)
                            self.updateDateEdit(start_date=self.bar_first_date, end_date=self.bar_second_date)
                else:
                    print('C')
                    self.plot_trade_performance(self.account_data)
                    self.plot_line_graph(self.account_data)
                    self.plot_calendar(self.account_data)
                    self.updateDateEdit()
            if show == 'calendar' and data is None:
                if self.filtered_data is not None:
                    self.plot_calendar(self.filtered_data)
                else:
                    self.plot_calendar(self.account_data)
                self.add_new_trade_button.setVisible(True)
        except Exception as e:
            print(f'Failed to change second stack: {e}')

    def second_changes_first_to_screenshot(self, qwidget=None):
        try:
            if qwidget is not None:
                qwidget.set_pixmap_width(self.first_graph_stack.width())
                self.first_graph_stack.addWidget(qwidget)
                self.first_graph_stack.setCurrentWidget(qwidget)
            else:
                label = QLabel('Click a screenshot to display here.')
                label.setStyleSheet("color: white;")
                label.setAlignment(Qt.AlignCenter)
                self.first_graph_stack.addWidget(label)
                self.first_graph_stack.setCurrentWidget(label)
        except Exception as e:
            print(f'Second changes first error: {e}')

    def second_changes_third_to_notes(self, trade_id):
        self.trade_note_view = CustomNoteView(trade_id=trade_id)
        self.third_graph_stack.addWidget(self.trade_note_view)
        self.third_graph_stack.setCurrentWidget(self.trade_note_view)

    def second_stack_go_back_pressed(self):
        self.reload_stacks(show='bar_graph')

    def third_stack_go_back_pressed(self):
        self.reload_stacks(show='calendar')
        self.updateWhenDayClicked(first_date=self.first_date, second_date=self.second_date)
        self.updateDateEdit(start_date=self.first_date, end_date=self.second_date)
        self.first_date, self.second_date, self.daily_note_view = None, None, None

    def third_stack_day_clicked(self, account_id, date):
        try:
            self.add_new_trade_button.setVisible(False)
            self.new_trade_button_changes_second_stats(visible=False)
            self.first_date, self.second_date = self.first_dateEdit.date().toString(
                "yyyy-MM-dd"), self.second_dateEdit.date().toString("yyyy-MM-dd")

            self.updateWhenDayClicked(date)
            self.daily_note_view = CustomNoteView(account_id=account_id, date=date)
            self.daily_note_view.first_date, self.daily_note_view.second_date = self.first_dateEdit.date(), self.second_dateEdit.date()
            self.daily_note_view.go_back_button_pressed.connect(self.third_stack_go_back_pressed)
            self.third_graph_stack.addWidget(self.daily_note_view)
            self.third_graph_stack.setCurrentWidget(self.daily_note_view)
        except Exception as e:
            print(f'Failed to change third stack into note view: {e}')

    def start_data_fetching(self):
        # Code to start fetching data
        print("Starting data fetching for Personal Accounts")

    def stop_data_fetching(self):
        # Code to stop fetching data
        print("Stopping data fetching for Personal Accounts")

    def showEvent(self, event):
        super().showEvent(event)
        self.start_data_fetching()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.stop_data_fetching()

    def animate_new_trade_popup(self, show=True):
        try:
            if show:
                self.new_trade_popup.setWindowOpacity(0)
                self.new_trade_popup.show()
                self.center_new_trade_popup()
                self.disable_account_list_signal.emit()
                self.new_trade_animation = QPropertyAnimation(self.new_trade_popup, b"windowOpacity")
                self.new_trade_animation.setDuration(500)
                self.new_trade_animation.setStartValue(0)
                self.new_trade_animation.setEndValue(1)
                self.new_trade_animation.start()
                self.new_trade_animation.start()
            else:
                if self.new_trade_popup is not None:
                    self.new_trade_animation = QPropertyAnimation(self.new_trade_popup, b"windowOpacity")
                    self.new_trade_animation.setDuration(500)
                    self.new_trade_animation.setStartValue(1)
                    self.new_trade_animation.setEndValue(0)
                    self.new_trade_animation.finished.connect(self.new_trade_popup.hide)
                    self.new_trade_animation.start()
                    self.new_trade_popup = None
        except Exception as e:
            print(f'Failed to animate new_trade pop up: {e}')


def clearLayout(layout):
    plt.close()
    for i in reversed(range(layout.count())):
        widget_to_remove = layout.itemAt(i).widget()
        if widget_to_remove:
            layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def trades_to_dataframe(trades):
    df = pd.DataFrame(trades)
    df['entry_time'] = pd.to_datetime(df['entry_time'])
    df['exit_time'] = pd.to_datetime(df['exit_time'])
    return df
