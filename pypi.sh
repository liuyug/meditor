rm -rf build
rm dist/*.whl

python3 setup.py bdist_wheel
twine upload dist/*.whl
