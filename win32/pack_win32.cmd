cls

set PATH=%PATH%;C:\Python35-32\Lib\site-packages\PyQt5\Qt\bin

pushd ..

rmdir build /s /q
rmdir dist\rsteditor /s /q

pyinstaller --clean --noconfirm %1 rsteditor.spec

popd
