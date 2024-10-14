import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
)

class InstallerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set window title and size
        self.setWindowTitle('Application Installer')
        self.setGeometry(500, 300, 400, 200)

        # Create layout
        layout = QVBoxLayout()

        # Label
        self.label = QLabel('Welcome to the Application Installer!', self)
        layout.addWidget(self.label)

        # Install Button
        self.install_button = QPushButton('Install Application', self)
        self.install_button.clicked.connect(self.install_app)
        layout.addWidget(self.install_button)

        # Set layout
        self.setLayout(layout)

    def install_app(self):
        # Prompt user to select installation folder
        install_directory = QFileDialog.getExistingDirectory(self, "Select Install Directory")

        if install_directory:
            try:
                # Assuming 'my_app.exe' is the file to be copied (you can replace it with your .exe file)
                source_file = os.path.join(os.getcwd(), 'my_app.exe')

                if not os.path.exists(source_file):
                    QMessageBox.critical(self, 'Error', f"Source file {source_file} not found.")
                    return

                destination = os.path.join(install_directory, 'my_app.exe')

                # Copy file to the selected directory
                shutil.copy(source_file, destination)

                QMessageBox.information(self, 'Success', f'Application installed successfully in {install_directory}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to install application: {str(e)}')
        else:
            QMessageBox.warning(self, 'Canceled', 'Installation canceled.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InstallerWindow()
    window.show()
    sys.exit(app.exec_())
