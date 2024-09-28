import os
from decimal import Decimal
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import pandas as pd
from bottom_frame.image_drop import InteractiveDropArea
from SQL import (insert_or_update_zone_with_screenshot, get_zone_scores, get_all_screenshots)
from PIL import Image
import io
from bottom_frame.custom_widgets import LimitedTextEdit


class TradeInfoInputView(QWidget):

    def __init__(self, parent=None, data=None, note_view=None):
        super(TradeInfoInputView, self).__init__(parent)
        self.server_note_id = None
        self.data = data
        self.total_score = 0
        self.trade_id = int(data['trade_id'])
        self.note_entry_view = note_view
        self.zone_scores = get_zone_scores(self.trade_id)
        self.server_screenshots = get_all_screenshots(self.trade_id)

        self.setupView()
        self.setStyleSheet("""
        QWidget {
            background-color: #222222;
            color: white;
        }""")

    def setupView(self):
        try:
            layout = QVBoxLayout(self)
            self.setLayout(layout)

            self.top_button_frame = QFrame()
            self.top_button_layout = QHBoxLayout(self.top_button_frame)

            self.go_back_button = QPushButton('Back')
            self.go_back_button.setStyleSheet("""
                        QPushButton:hover {
                            background-color: #2c7e33;
                        }""")
            self.title = QLabel('Screenshot & Score')
            self.save_info_button = QPushButton('Save', clicked=self.save_trade)
            self.save_info_button.setStyleSheet("""
                        QPushButton:hover {
                            background-color: #2c7e33;
                        }""")
            self.top_button_layout.addWidget(self.go_back_button)
            self.top_button_layout.addWidget(self.title)
            self.top_button_layout.addWidget(self.save_info_button)
            self.setupTradeInfo()
            self.setupInputs()
            layout.addWidget(self.top_button_frame)
            layout.addWidget(self.trade_info_frame)
            layout.addWidget(self.input_frame)
        except Exception as e:
            print(f'Error setting up view: {e}')

    def save_trade(self):
        try:
            def apply_green_tint(image_data):
                image = Image.open(io.BytesIO(image_data)).convert("RGBA")
                green_tint = Image.new('RGBA', image.size, (195, 220, 155, 100))
                tinted_image = Image.alpha_composite(image, green_tint)
                with io.BytesIO() as output:
                    tinted_image.save(output, format="PNG")
                    return output.getvalue()

            server_screenshots = get_all_screenshots(self.trade_id)
            screenshots = []
            for label, area in zip(['HTF', 'ITF', 'LTF'],
                                   [self.screenshot_areas['HTF'], self.screenshot_areas['ITF'],
                                    self.screenshot_areas['LTF']]):
                try:
                    current_screenshot_path = area.file_path
                    if current_screenshot_path:
                        if isinstance(current_screenshot_path, (str, os.PathLike)):
                            with open(current_screenshot_path, 'rb') as file:
                                current_screenshot_data = file.read()
                        elif isinstance(current_screenshot_path, (memoryview, bytes)):
                            current_screenshot_data = current_screenshot_path
                        else:
                            print(f"Unsupported screenshot type for label {label}: {type(current_screenshot_path)}")
                            continue

                        if not server_screenshots or server_screenshots[label] != current_screenshot_data:
                            tinted_screenshot = apply_green_tint(current_screenshot_data)
                            area.set_screenshot(tinted_screenshot)
                            area.clickable = False
                            screenshots.append((label, current_screenshot_data))
                except Exception as e:
                    print(f"Failed to read screenshot: {e}")
                    return

            cb_score_entries = [
                ('strength', self.combo_boxes['strength'], int),
                ('basetime', self.combo_boxes['basetime'], float),
                ('freshness', self.combo_boxes['freshness'], int),
                ('trend', self.combo_boxes['trend'], int),
                ('curve', self.combo_boxes['curve'], float),
                ('profitzone', self.combo_boxes['profitzone'], int),
            ]
            changed_scores = {}
            for score_name, combo_box, score_type in cb_score_entries:
                combo_box_score = score_type(self.get_score_from_combobox(combo_box))
                if self.zone_scores is not None and score_name in self.zone_scores:
                    server_score = self.zone_scores[score_name]
                else:
                    server_score = None
                combo_box.setEnabled(False)
                if server_score != combo_box_score:
                    current_index = combo_box.currentIndex()
                    if current_index != 0:
                        changed_scores[score_name] = combo_box_score
                        combo_box.setStyleSheet("""
                            QComboBox {
                                color: #c3dc9b;  
                            }""")
                    else:
                        combo_box.setStyleSheet("""
                            QComboBox {
                                color: #ff4c4c;  
                            }""")
                else:
                    combo_box.setStyleSheet("""
                            QComboBox {
                                color: #ff4c4c;  
                            }""")

            current_note_text = self.note_entry_view.get_note_text()
            self.note_entry_view.notes_entry_box.setEnabled(False)
            if current_note_text != "" and current_note_text != self.note_entry_view.server_note:
                self.note_entry_view.notes_entry_box.setStyleSheet("background-color: rgba(195, 220, 155, 0.3);")
            elif current_note_text == "":
                self.note_entry_view.notes_entry_box.setStyleSheet("background-color: rgba(255, 76, 76, 0.3);")
            else:
                self.note_entry_view.notes_entry_box.setStyleSheet("""
                        QWidget {
                            background-color: #222222;
                            color: white;
                        }
                    """)

            cancel_button = QPushButton("Cancel")
            cancel_button.setStyleSheet("""
                        QPushButton:hover {
                            background-color: #ff4c4c;
                        }
                        QPushButton {
                            border: 2px solid #ff7f7f;
                        }""")

            def cancel_button_pressed():
                try:
                    self.save_info_button.setText("Save")
                    self.save_info_button.disconnect()
                    self.save_info_button.clicked.connect(self.save_trade)

                    if cancel_button:
                        self.top_button_layout.removeWidget(cancel_button)
                        cancel_button.deleteLater()

                    for score_name, combo_box in self.combo_boxes.items():
                        combo_box.setStyleSheet("""
                            QComboBox {
                                color: #white;  
                            }""")
                        combo_box.setEnabled(True)

                    self.note_entry_view.notes_entry_box.setEnabled(True)
                    self.note_entry_view.notes_entry_box.setStyleSheet("""
                        QWidget {
                            background-color: #222222;
                            color: white;
                        }
                    """)
                    for label, area in zip(['HTF', 'ITF', 'LTF'],
                                           [self.screenshot_areas['HTF'], self.screenshot_areas['ITF'],
                                            self.screenshot_areas['LTF']]):
                        for label2, screenshot_data in screenshots:
                            if label == label2:
                                area.set_screenshot(screenshot_data)
                                area.clickable = True
                except Exception as e:
                    print(f'Failed to cancel button action: {e}')

            self.save_info_button.setText("Confirm")
            self.top_button_layout.addWidget(cancel_button)
            cancel_button.clicked.connect(cancel_button_pressed)

            def confirm_button_pressed():
                insert_or_update_zone_with_screenshot(self.trade_id, changed_scores, screenshots, current_note_text)
                cancel_button_pressed()

            self.save_info_button.disconnect()
            self.save_info_button.clicked.connect(confirm_button_pressed)

        except Exception as e:
            print(f'Error saving trade information: {e}')

    def setupTradeInfo(self):
        try:
            self.trade_info_frame = QFrame()
            self.trade_info_layout = QHBoxLayout(self.trade_info_frame)
            self.trade_info_layout.setAlignment(Qt.AlignCenter)

            if isinstance(self.data, pd.Series):
                self.first_label = QLabel(f"Date: {self.data['entry_time'].strftime('%m-%d-%Y')}\n"
                                          f"Entry Time: {self.data['entry_time'].strftime('%H:%M')}\n"
                                          f"Exit Time: {self.data['exit_time'].strftime('%H:%M')}")
                self.second_label = QLabel(f"Instrument: {self.data['instrument']}\n"
                                           f"Direction: {self.data['direction']}\n"
                                           f"Profit: {self.data['profit']:.2f}")

                self.trade_info_layout.addWidget(self.first_label)
                self.trade_info_layout.addWidget(self.second_label)
        except Exception as e:
            print(f'Error setting up trade info: {e}')

    def setupInputs(self):
        try:
            self.input_frame = QFrame()
            self.input_layout = QHBoxLayout(self.input_frame)

            self.screenshot_frame = QFrame()
            self.screenshot_layout = QVBoxLayout(self.screenshot_frame)

            self.screenshot_areas = {}
            for label in ['HTF', 'ITF', 'LTF']:
                self.screenshot_areas[label] = InteractiveDropArea(trade_id=int(self.trade_id), screenshot_index=label)
                self.screenshot_layout.addWidget(self.screenshot_areas[label])

            for i in range(len(self.screenshot_areas)):
                self.screenshot_layout.setStretch(i, 1)

            self.score_frame = QFrame()
            self.score_layout = QVBoxLayout(self.score_frame)

            self.score_label = QLabel(f'Total score: {self.total_score}')
            score_entries = {
                'strength': (['Strength', '0', '1', '2']),
                'basetime': (['Base Time', '0.0', '0.5', '1.0']),
                'freshness': (['Freshness', '0', '1', '2']),
                'trend': (['Trend', '0', '1', '2']),
                'curve': (['Curve', '0.0', '0.5', '1.0']),
                'profitzone': (['Profit Zone', '0', '1', '2']),
            }

            self.combo_boxes = {}
            for score_name, items in score_entries.items():
                combo_box = QComboBox()
                combo_box.addItems(items)
                combo_box.setCurrentIndex(0)
                combo_box.model().item(0).setEnabled(False)
                combo_box.currentIndexChanged.connect(self.update_total_score)
                self.combo_boxes[score_name] = combo_box
                self.score_layout.addWidget(combo_box)

            if self.zone_scores:
                try:
                    for score_name, combo_box in self.combo_boxes.items():
                        if score_name in self.zone_scores:
                            score_value = self.zone_scores[score_name]
                            if isinstance(score_value, Decimal):
                                if score_value == Decimal('0.5'):
                                    score_value = 0.5
                                elif score_value == Decimal('1.0'):
                                    score_value = 1.0
                                elif score_value == Decimal('0.0'):
                                    score_value = 0.0
                                else:
                                    score_value = float(score_value)
                            combo_box.setCurrentIndex(combo_box.findText(str(score_value)))
                except Exception as e:
                    print(f'Error loading zone scores from server: {e}')

            self.score_layout.addWidget(self.score_label)
            self.input_layout.addWidget(self.screenshot_frame)
            self.input_layout.addWidget(self.score_frame)
        except Exception as e:
            print(f'Error setting up inputs: {e}')

    def update_total_score(self):
        try:
            self.total_score = 0
            for score_name, combo_box in self.combo_boxes.items():
                score_value = self.get_score_from_combobox(combo_box)
                self.total_score += score_value

            self.score_label.setText(f'Total score: {self.total_score:.1f}')
        except Exception as e:
            print(f"Error updating total score: {e}")

    def get_score_from_combobox(self, combobox):
        try:
            current_text = combobox.currentText()
            return float(current_text)
        except ValueError:
            return 0.0



