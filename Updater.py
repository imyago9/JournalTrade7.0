import os
import shutil
import time

# Paths
user_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), '.JTbyY', 'JournalTrade')
OLD_EXE_PATH = os.path.join(user_data_dir, 'JournalTrade.exe')
NEW_EXE_PATH = os.path.join(user_data_dir, 'JournalTrade_new.exe')

def main():
    # Wait for a moment to ensure the main application is closed
    time.sleep(2)

    # Replace the old executable with the new one
    if os.path.exists(OLD_EXE_PATH):
        os.remove(OLD_EXE_PATH)
    shutil.move(NEW_EXE_PATH, OLD_EXE_PATH)

    # Restart the application
    os.startfile(OLD_EXE_PATH)

if __name__ == "__main__":
    main()
