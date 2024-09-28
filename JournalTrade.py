import requests
import os
from PyQt5.QtWidgets import QMessageBox, QApplication
import LOGIN
import sys
import shutil
import subprocess
from appdirs import AppDirs

user_data_dir = dirs.user_data_dir

if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

data_path = os.path.join(user_data_dir, 'data')
if not os.path.exists(data_path):
    os.makedirs(data_path)


# URLs
GITHUB_VERSION_URL = 'https://raw.githubusercontent.com/imyago9/JournalTrade4.1/master/version.txt'
JOURNALTRADE_EXE_URL = 'https://raw.githubusercontent.com/imyago9/JournalTrade4.1/master/dist/JournalTrade.exe'
INSTALLER_EXE_URL = 'https://raw.githubusercontent.com/imyago9/JournalTrade4.1/master/dist/Installer.exe'
LOCAL_VERSION_PATH = os.path.join(user_data_dir, 'version.txt')
LOCAL_EXE_PATH = os.path.join(user_data_dir, 'JournalTrade.exe')
NEW_EXE_PATH = os.path.join(user_data_dir, 'JournalTrade_new.exe')
UPDATER_EXE_PATH = os.path.join(user_data_dir, 'Installer.exe')


def get_github_version(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching version from GitHub: {e}")
        return None


def get_local_version(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Local version file not found at {file_path}")
        return None

def download_file(url, dest_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Downloaded {url} to {dest_path}")
    except requests.RequestException as e:
        print(f"Error downloading file from {url}: {e}")

def download_text_file(url, dest_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(dest_path, 'w') as f:
            f.write(response.text.strip())
        print(f"Downloaded {url} to {dest_path}")
    except requests.RequestException as e:
        print(f"Error downloading file from {url}: {e}")
        raise

def update_application():
    # Download the new executable
    download_file(JOURNALTRADE_EXE_URL, NEW_EXE_PATH)

    if os.path.exists(UPDATER_EXE_PATH):
        os.remove(UPDATER_EXE_PATH)
    download_file(INSTALLER_EXE_URL, UPDATER_EXE_PATH)

    # Download and update the local version file
    download_text_file(GITHUB_VERSION_URL, LOCAL_VERSION_PATH)

    # Run the updater executable and exit the current application
    subprocess.Popen([UPDATER_EXE_PATH])
    sys.exit()

def check_for_updates():
    github_version = get_github_version(GITHUB_VERSION_URL)
    local_version = get_local_version(os.path.join(os.getenv('LOCALAPPDATA'), 'Y', 'JournalTrade', 'version.txt'))

    if github_version and local_version and github_version != local_version:
        reply = QMessageBox.question(None, 'Update Available',
                                     'A new version of JournalTrade is available. Do you want to update?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            update_application()
        else:
            sys.exit()
    elif local_version is None:
        update_application()
    elif github_version == local_version:
        print(f'Version Match! GitHub Version: {github_version}. Local Version: {local_version}')
        print('Opening Application.')
        LOGIN.main()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    check_for_updates()
