cls

pushd ..

rmdir build /s /q
rmdir dist\rsteditor /s /q

pyinstaller --clean --noconfirm rsteditor.spec

popd
