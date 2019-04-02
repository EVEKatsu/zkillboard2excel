pip install -r requirements.txt
npm install
./node_modules/.bin/electron-rebuild
pyinstaller api.py

rm -rf .DS_Store
rm -rf __pycache__
rm -rf api.spec
rm -rf build/

./node_modules/.bin/electron-packager . --overwrite --icon="zkillboard2excel.icns" --ignore=".vscode" --ignore=".python-version" --ignore="export" --ignore="sde" --ignore="sde.zip" --ignore="settings.json" --ignore="cached.json" --ignore="make.sh" --ignore="make.bat"
