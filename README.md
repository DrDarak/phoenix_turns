# phoenix_turns
Phoenix turns downloader

Python 3.9 (not 10 so QT5tools work)

pip install requests
pip install pyqt5
pip install pyinstaller

pyinstaller --icon=phoenix.ico --add-data="phoenix_32x32.png;." --add-data="phoenix.ico;." --noconsole main.py