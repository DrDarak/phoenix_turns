# phoenix_turns
Phoenix turns downloader. We are not finished enough to allow contributions but when it's complete in my mind we can go that direction.

Requires:
Python 3.9 (not 10 so QT5tools work)
pip install requests
pip install pyqt5
pip install pyinstaller

#ignore installer info
pyinstaller --icon=phoenix.ico --add-data="phoenix_32x32.png;." --add-data="phoenix.ico;." --noconsole main.py