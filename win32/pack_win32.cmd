cls

rem check module: modulegraph run.py

pushd ..

rmdir build /s /q
rmdir dist\meditor /s /q

pyinstaller --clean --noconfirm --noconsole^
 --name meditor^
 --icon "meditor\data\meditor-text-editor.ico"^
 --add-data "meditor\data;data"^
 --exclude-module pandas^
 --exclude-module ipython^
 --exclude-module matplotlib^
 --exclude-module numpy^
 --exclude-module jedi^
 --exclude-module jinja2^
 --exclude-module lxml.etree^
 --exclude-module sqlalchemy^
 --exclude-module sqlite3^
 --exclude-module pydoc^
 --exclude-module pycparser^
 run.py

popd
