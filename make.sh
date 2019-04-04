# pip install -r requirements.txt
# npm install
# ./node_modules/.bin/electron-rebuild

rm -rf dist/

pyinstaller api.py

rm -rf .DS_Store
rm -rf __pycache__
rm -rf api.spec
rm -rf build/

./node_modules/.bin/electron-packager . --overwrite --icon="icon.icns" --ignore=".vscode" --ignore=".python-version" --ignore="sde" --ignore="sde.zip" --ignore="settings.json" --ignore="cached.json"
