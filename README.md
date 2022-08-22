# phoenix_turns
Phoenix turns downloader. We are not finished enough to allow contributions but when it's complete in my mind we can go that direction.

Requires:
<ul>
<li>Python 3.9 (not 10 so QT5tools work)
<li>pip install requests
<li>pip install pyqt5
<li>pip install pyinstaller
<li>pip install nx_freeze
<li>NullScript Scriptable Install System (NSIS)
</ul>

#Release Method
<ul>
<li> Change version numbers in setup.py / setup.nis
<li> run: python setup.py build_exe
<li> drop: setup.nis into NSIS app
</ul>
 