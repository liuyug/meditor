cls

pushd ..

rmdir build /s /q
del dist\*.whl /q

python setup.py bdist_wheel
twine.exe upload dist\*.whl

popd
