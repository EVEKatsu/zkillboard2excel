@echo off

chcp 65001

rem pip install virtualenvwrapper-win
rem mkvirtualenv envname
rem workon envname
rem pip install -r requirements.txt

rem set TMP_PATH=%PATH%
rem set PATH=C:\Python27;%PATH%

rem npm install
rem .\node_modules\.bin\electron-rebuild

rem set PATH=%TMP_PATH%

rd /s /q dist

pyinstaller api.py

rd /s /q __pycache__
rd /s /q api.spec
rd /s /q build

.\node_modules\.bin\electron-packager . --overwrite --icon="icon.ico" --ignore=".vscode" --ignore=".python-version" --ignore="sde" --ignore="sde.zip" --ignore="settings.json" --ignore="cached.json"
