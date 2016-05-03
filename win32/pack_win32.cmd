cls

pushd ..

rmdir build /s /q

pyinstaller --clean --noconfirm rsteditor.spec

popd
