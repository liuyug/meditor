cls

set PATH=%PATH%;C:\Python35-32\Lib\site-packages\PyQt5\Qt\bin

pushd ..

rmdir build /s /q
rmdir dist\meditor /s /q

pyinstaller --clean --noconfirm --noconsole --name meditor --icon "meditor\share\pixmaps\meditor-text-editor.ico" --add-data "meditor\share;share" run.py

popd
