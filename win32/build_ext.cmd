cls

pushd ..

rmdir build /s /q

python setup.py build_ext --inplace

popd
